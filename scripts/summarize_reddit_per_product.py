import json
import os
from collections import Counter
from trust_score import calculate_trust_score

def summarize_with_tags(comments):
    pros = Counter()
    cons = Counter()

    for comment in comments:
        tags = comment.get("tags") or []
        if not isinstance(tags, list):
            tags = []

        sentiment = comment.get("sentiment")
        for tag in tags:
            if sentiment == "positive":
                pros[tag] += 1
            elif sentiment == "negative":
                cons[tag] += 1

    return {
        "top_pros": [tag for tag, _ in pros.most_common(5)],
        "top_cons": [tag for tag, _ in cons.most_common(5)]
    }

def load_reddit_data(path="data/reddit_cpg_sentiment_threads_summary_ready.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def summarize_reddit_by_product(data):
    product_groups = {}
    for post in data:
        product = post.get("product") or post.get("thread_id")
        if product not in product_groups:
            product_groups[product] = []
        product_groups[product].extend(post.get("comments", []))

    summaries = []
    for product, comments in product_groups.items():
        tag_summary = summarize_with_tags(comments)
        trust = calculate_trust_score(comments)

        summaries.append({
            "product": product,
            "top_pros": tag_summary["top_pros"],
            "top_cons": tag_summary["top_cons"],
            "trust_score": trust["score"],
            "confidence": trust["confidence"],
            "total_comments": len(comments)
        })

    return summaries

def save_to_json(data, output="data/trustlayer_reddit_summary.json"):
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Reddit summary saved to: {output}")
