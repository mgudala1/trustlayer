import json
from transformers import pipeline
import os

# Load summarization model (T5-small)
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def classify_sentiment(text):
    positive_keywords = ["love", "great", "helpful", "excellent", "perfect", "amazing"]
    negative_keywords = ["hate", "bad", "terrible", "waste", "awful", "broke"]
    text_lower = text.lower()
    if any(word in text_lower for word in positive_keywords):
        return "positive"
    elif any(word in text_lower for word in negative_keywords):
        return "negative"
    else:
        return "neutral"

input_path = "data/reddit_sample.json"
output_path = "plugin/data/categories/skincare.json"

with open(input_path, "r") as f:
    raw_comments = json.load(f)

structured_data = []
max_comments = 10
count = 0

for post in raw_comments:
    post_permalink = post.get("permalink", "https://reddit.com")
    post_timestamp = post.get("created_utc", "2025-06-21T12:00:00Z")
    for comment in post.get("comments", []):
        if count >= max_comments:
            break
        feedback = comment.get("body", "").strip()
        print(f"[DEBUG] Feedback: {feedback[:60]}")
        if not feedback:
            continue
        try:
            # Generate summary
            summary = summarizer("summarize: " + feedback, max_length=30, min_length=5, do_sample=False)[0]["summary_text"]
        except Exception as e:
            print(f"[ERROR] Could not summarize: {feedback[:50]}... Error: {e}")
            summary = "Summary failed"
        # Generate sentiment
        sentiment = classify_sentiment(feedback)
        # Build schema entry
        structured_entry = {
            "product_id": "cerave_foaming_cleanser",
            "source": "reddit",
            "timestamp": comment.get("created_utc", post_timestamp),
            "feedback_text": feedback,
            "sentiment_label": sentiment,
            "authenticity_score": 0.85,
            "summary_text": summary,
            "metadata": {
                "username_hash": "sha256:placeholder",
                "upvotes": comment.get("score", 0),
                "permalink": post_permalink
            },
            "tags": ["skincare"]
        }
        structured_data.append(structured_entry)
        count += 1
    if count >= max_comments:
        break

# Save to skincare.json
os.makedirs("plugin/data/categories", exist_ok=True)
with open(output_path, "w") as f:
    json.dump(structured_data, f, indent=2)

print(f"[OK] Wrote {len(structured_data)} structured entries to {output_path}")
