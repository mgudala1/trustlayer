import json
import os
import sys
from youtube_comment_downloader import YoutubeCommentDownloader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect

analyzer = SentimentIntensityAnalyzer()

# 🧠 Sentiment Analysis
def get_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score > 0.2:
        return "positive"
    elif score < -0.2:
        return "negative"
    else:
        return "neutral"

# 🏷 Keyword Tagging
def extract_tags(text):
    text = text.lower()
    tags = []
    if "smell" in text or "scent" in text:
        tags.append("smell")
    if "rash" in text or "irritation" in text:
        tags.append("rash")
    if "acne" in text:
        tags.append("acne")
    if "lasts long" in text or "fades quickly" in text:
        tags.append("lasting power")
    if "cheap" in text or "expensive" in text:
        tags.append("price")
    return tags

# 🚨 Spam / Fake Review Filter
def is_suspicious(text):
    text = text.lower()
    red_flags = ["life changing", "miracle", "best product ever", "click here", "link in bio"]
    repetitive = len(set(text.split())) < 3
    has_flags = any(flag in text for flag in red_flags)
    return repetitive or has_flags

# 🌍 Language Detection
def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False

# 💬 Extract Comments and Optional Replies
def scrape_comments(video_url, max_comments=100):
    downloader = YoutubeCommentDownloader()
    comments = []

    try:
        for comment in downloader.get_comments_from_url(video_url):
            # ✅ Skip anything that’s not a dictionary
            if not isinstance(comment, dict):
                print(f"⚠️ Skipped non-dictionary comment object: {comment}")
                continue

            text = comment.get("text", "")
            if not isinstance(text, str) or not is_english(text) or is_suspicious(text):
                continue

            # Detect sentiment, tags
            sentiment = get_sentiment(text)
            tags = extract_tags(text)

            # Extract replies (if any)
            replies = []
            for reply in comment.get("replies", []):
                if not isinstance(reply, dict):
                    print(f"⚠️ Skipped non-dictionary reply object: {reply}")
                    continue
                r_text = reply.get("text", "")
                if not isinstance(r_text, str) or not is_english(r_text) or is_suspicious(r_text):
                    continue
                reply_sentiment = get_sentiment(r_text)
                replies.append({
                    "text": r_text,
                    "author": reply.get("author"),
                    "sentiment": reply_sentiment
                })

            comments.append({
                "comment_id": comment.get("cid"),
                "text": text,
                "author": comment.get("author"),
                "likes": comment.get("votes"),
                "time": comment.get("time"),
                "is_pinned": comment.get("isPinned", False),
                "sentiment": sentiment,
                "tags": tags,
                "replies": replies
            })

            if len(comments) >= max_comments:
                break
    except Exception as e:
        print("❌ Error scraping comments:", e)

    return comments

def save_comments(video_id, comments):
    os.makedirs("../data", exist_ok=True)
    path = f"../data/{video_id}_comments.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(comments, f, indent=2)
    print(f"✅ Saved {len(comments)} comments to: {path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python youtube_scraper.py <video_url>")
        return
    video_url = sys.argv[1]
    video_id = video_url.split("v=")[-1]
    comments = scrape_comments(video_url, 100)
    save_comments(video_id, comments)

if __name__ == "__main__":
    main()
# This script scrapes YouTube comments, analyzes sentiment, extracts tags, filters spam, and saves the results.