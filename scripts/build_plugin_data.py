import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# Load full thread data
with open("data/reddit_cpg_sentiment_threads.json", "r", encoding="utf-8") as f:
    threads = json.load(f)

def clean_comment(text):
    if not text or text.lower() in ["[deleted]", "[removed]"]:
        return ""
    return ' '.join(text.split())

def extract_top_comments(thread):
    return [c for c in thread["comments"] if isinstance(c, dict)]

def extract_pros_cons(thread):
    pros, cons = [], []
    for comment in extract_top_comments(thread):
        text = clean_comment(comment["body"])
        if not text:
            continue
        score = analyzer.polarity_scores(text)["compound"]
        if score >= 0.5:
            pros.append((score, text))
        elif score <= -0.5:
            cons.append((score, text))
    pros = sorted(pros, reverse=True)[:5]
    cons = sorted(cons)[:5]
    return [p[1] for p in pros], [c[1] for c in cons]

def compute_auth_score(post, pros, cons):
    score = 0
    score += 30 if post["score"] > 50 else 20 if post["score"] > 10 else 10
    score += 30 if post["num_comments"] > 30 else 20 if post["num_comments"] > 10 else 10
    score += 20 if len(pros) >= 3 else 10
    score += 20 if len(cons) <= 2 else 10
    return min(score, 100)

# Process and build final plugin-ready data
results = []
for post in threads:
    pros, cons = extract_pros_cons(post)
    auth_score = compute_auth_score(post, pros, cons)
    results.append({
        "title": post["title"],
        "permalink": post["permalink"],
        "auth_score": auth_score,
        "pros": pros,
        "cons": cons
    })

# Save to final output
output_path = "data/trustlayer_plugin_data.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"✅ Done! Saved {len(results)} items to {output_path}")
# This script processes Reddit threads to extract pros and cons, computes an author trust score,