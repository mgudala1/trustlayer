import json
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# 📂 Load Reddit threads from JSON file
def load_threads(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 🧹 Clean each comment body
def clean_comment(text):
    if not text or text.lower() in ["[deleted]", "[removed]"]:
        return ""
    return ' '.join(text.split())  # remove excess spaces, line breaks

# 🔁 Flatten all top-level comments (no recursive replies for now)
def extract_all_top_comments(thread):
    return [c for c in thread["comments"] if isinstance(c, dict)]

# 💡 Tag top 5 pros and cons by sentiment
def process_comments(thread):
    pros, cons = [], []

    for comment in extract_all_top_comments(thread):
        text = clean_comment(comment["body"])
        if not text:
            continue

        score = analyzer.polarity_scores(text)["compound"]

        if score >= 0.5:
            pros.append((score, text))
        elif score <= -0.5:
            cons.append((score, text))

    # Sort by sentiment strength
    pros = sorted(pros, reverse=True)[:5]
    cons = sorted(cons)[:5]

    return [p[1] for p in pros], [c[1] for c in cons]

# 📦 Main pipeline
def main():
    input_path = "reddit_cpg_sentiment_threads.json"
    output_path = "reddit_pros_cons.json"

    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return

    threads = load_threads(input_path)
    processed = []

    for t in threads:
        pros, cons = process_comments(t)
        processed.append({
            "title": t["title"],
            "permalink": t["permalink"],
            "pros": pros,
            "cons": cons
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

    print(f"✅ Saved pros/cons summary to: {output_path}")

# ▶️ Run
if __name__ == "__main__":
    main()
# This script analyzes Reddit threads to extract top pros and cons based on sentiment.