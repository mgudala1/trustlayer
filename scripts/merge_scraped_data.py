import os
import json
import pandas as pd

def merge_scraped_youtube_comments(data_dir="../data"):
    merged = []
    for filename in os.listdir(data_dir):
        if filename.endswith("_comments.json"):
            path = os.path.join(data_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                try:
                    comments = json.load(f)
                    for comment in comments:
                        comment["source"] = "youtube"
                        comment["video_id"] = filename.replace("_comments.json", "")
                        merged.append(comment)
                except Exception as e:
                    print(f"⚠️ Skipping {filename}: {e}")
    print(f"✅ Merged {len(merged)} comments")
    return pd.DataFrame(merged)

if __name__ == "__main__":
    df = merge_scraped_youtube_comments()
    print(df.head())
