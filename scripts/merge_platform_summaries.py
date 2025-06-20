import json

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def merge_summaries(youtube_data, reddit_data):
    summary_dict = {}

    for y in youtube_data:
        product = y["product"]
        summary_dict.setdefault(product, {})["youtube"] = {
            "trust_score": y.get("trust_score"),
            "top_pros": y.get("top_pros", []),
            "top_cons": y.get("top_cons", []),
            "total_comments": y.get("total_comments", 0)
        }

    for r in reddit_data:
        product = r["product"]
        summary_dict.setdefault(product, {})["reddit"] = {
            "trust_score": r.get("trust_score"),
            "top_pros": r.get("top_pros", []),
            "top_cons": r.get("top_cons", []),
            "total_comments": r.get("total_comments", 0)
        }

    return [{"product": product, **data} for product, data in summary_dict.items()]

def save_combined_summary(data, output_path="data/trustlayer_combined_summary.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Combined summary saved to: {output_path}")
