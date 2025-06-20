# scripts/summarize_per_product.py

import os
import json
from collections import Counter
from trust_score import calculate_trust_score

def group_comments_by_product(df):
    product_groups = {}
    for _, row in df.iterrows():
        product_id = row.get("product") or row.get("video_id")  # fallback
        if product_id not in product_groups:
            product_groups[product_id] = []
        product_groups[product_id].append(row)
    return product_groups

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

def summarize_products(df):
    product_groups = group_comments_by_product(df)
    summaries = []

    for product_id, comments in product_groups.items():
        tag_summary = summarize_with_tags(comments)
        trust = calculate_trust_score(comments)

        summary = {
            "product": product_id,
            "top_pros": tag_summary["top_pros"],
            "top_cons": tag_summary["top_cons"],
            "trust_score": trust["score"],
            "confidence": trust["confidence"],
            "total_comments": len(comments)
        }

        summaries.append(summary)

    return summaries

def save_summary_to_json(summaries, output_path="data/trustlayer_youtube_summary.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)
    print(f"✅ Summary saved to: {output_path}")
