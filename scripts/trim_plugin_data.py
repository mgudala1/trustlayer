import json

with open("data/trustlayer_combined_summary.json", "r") as f:
    all_data = json.load(f)

def get_confidence(entry, platform):
    return entry.get(platform, {}).get("confidence", 0)

# Sort by confidence (or trust_score)
sorted_data = sorted(
    all_data,
    key=lambda x: get_confidence(x, "youtube") + get_confidence(x, "reddit"),
    reverse=True
)

# Keep only top 50
top_50 = sorted_data[:50]

with open("plugin/data/trustlayer_plugin_data.json", "w") as f:
    json.dump(top_50, f, indent=2)

print("✅ Trimmed to top 50 products")
