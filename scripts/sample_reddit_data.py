import json
import os

input_path = "data/reddit_cpg_sentiment_threads.json"
output_path = "data/reddit_sample.json"

with open(input_path, "r") as f:
    data = json.load(f)

sample = data[:50]

with open(output_path, "w") as f:
    json.dump(sample, f, indent=2)

print(f"[OK] Wrote {len(sample)} entries to {output_path}")
