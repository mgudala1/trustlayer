import praw
import json
import time
import os

# 🔐 Reddit API Credentials
reddit = praw.Reddit(
    client_id="WknJiqMgTVV8vHk1rTO8uQ",
    client_secret="JY6sD_Hmdm0RnQ5egrUhaiDsH0HNRg",
    user_agent="trustlayer-scraper by u/Mgoud311"
)

# 🧹 Clean a single comment
def clean_comment(text):
    if not text or text.lower() in ["[deleted]", "[removed]"]:
        return ""
    return ' '.join(text.strip().split())

# 🔁 Recursive comment parser (with filtering)
def parse_comment(comment):
    body = clean_comment(comment.body)
    if len(body) < 10 or comment.score < 0:
        return None
    return {
        "body": body,
        "score": comment.score,
        "author": str(comment.author),
        "created_utc": comment.created_utc,
        "replies": [r for r in (parse_comment(reply) for reply in comment.replies) if r]
    }

# 📥 Fetch posts with comments from a subreddit
def fetch_posts(subreddit_name, post_limit=25, sort_type="hot"):
    subreddit = reddit.subreddit(subreddit_name)
    method = getattr(subreddit, sort_type)
    posts = []

    for post in method(limit=post_limit):
        if post.stickied or post.score < 1:
            continue

        try:
            post.comments.replace_more(limit=0)
        except Exception as e:
            print(f"⚠️ Failed to expand comments for {post.permalink}: {e}")
            continue

        parsed_comments = [parse_comment(c) for c in post.comments]
        parsed_comments = [c for c in parsed_comments if c]

        posts.append({
            "subreddit": subreddit_name,
            "title": post.title,
            "selftext": post.selftext,
            "author": str(post.author),
            "score": post.score,
            "num_comments": post.num_comments,
            "created_utc": post.created_utc,
            "permalink": f"https://www.reddit.com{post.permalink}",
            "comments": parsed_comments
        })

    return posts

# ✅ Subreddits to scrape (CPG-focused)
subreddits = [
    "SkincareAddiction", "AsianBeauty", "30PlusSkincare", "beauty", "tretinoin",
    "Coffee", "EatCheapAndHealthy", "Cooking", "nutrition", "MealPrepSunday",
    "Supplements", "Biohackers", "NewParents", "BeyondTheBump", "BabyBumps",
    "CleaningTips", "BuyItForLife", "Frugal", "ZeroWaste",
    "SkincareScience", "TheOrdinarySkincare", "Sephora"
]

# ▶️ Run the scraper
def main():
    sort_modes = ["hot", "top", "new"]
    all_data = []
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    for subreddit in subreddits:
        for sort in sort_modes:
            print(f"🔍 Scraping r/{subreddit} [{sort}]...")
            try:
                reddit.subreddit(subreddit).id  # force API check
                posts = fetch_posts(subreddit, post_limit=25, sort_type=sort)
                all_data.extend(posts)
            except Exception as e:
                print(f"⚠️ Skipping r/{subreddit} - Reason: {e}")
            time.sleep(1)

    output_path = os.path.join(output_dir, "reddit_cpg_sentiment_threads.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

    print(f"✅ Done! Saved {len(all_data)} threads to {output_path}")

if __name__ == "__main__":
    main()
# This script scrapes Reddit for posts and comments related to Consumer Packaged Goods (CPG) sentiment.