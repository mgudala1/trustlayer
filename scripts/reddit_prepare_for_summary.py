import json
import os
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# Tag keywords to look for in Reddit comments
KEYWORD_TAGS = {
    "acne": ["acne", "pimple", "breakout", "zit"],
    "rash": ["rash", "redness", "irritation"],
    "smell": ["smell", "scent", "fragrance"],
    "dry": ["dry", "flaky", "peeling"],
    "greasy": ["greasy", "oily"],
    "burn": ["burn", "sting", "tingle"],
    "allergy": ["allergy", "reaction", "itch"],
    "moisturizing": ["moisturizing", "hydrating", "smooth"],
    "clean": ["clean", "gentle", "non-comedogenic"]
}

def extract_tags(text):
    text = text.lower()
    tags = []
    for tag, keywords in KEYWORD_TAGS.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags

def detect_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.2:
        return "positive"
    elif score <= -0.2:
        return "negative"
    else:
        return "neutral"

def guess_product(title):
    title = title.lower()
    known_brands = ["cerave", "olipop", "claritin", "cheezit", "nyquil", "tide", "magnesium", "retinol", "nike"]
    for brand in known_brands:
        if brand in title:
            return brand
    return "unknown_product"

def process_reddit_threads(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        threads = json.load(f)

    result = []

    for post in threads:
        product = guess_product(post.get("title", ""))
        thread_id = post.get("id") or post.get("title", "")[:30]
        processed_comments = []

        for comment in post.get("comments", []):
            text = comment.get("body", "").strip()
            if not text or len(text) < 10:
                continue

            sentiment = detect_sentiment(text)
            tags = extract_tags(text)

            if sentiment == "neutral" and not tags:
                continue  # skip low-value neutral

            processed_comments.append({
                "text": text,
                "sentiment": sentiment,
                "tags": tags
            })

        if processed_comments:
            result.append({
                "product": product,
                "thread_id": thread_id,
                "comments": processed_comments
            })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Prepared {len(result)} threads for summarization → {output_path}")
