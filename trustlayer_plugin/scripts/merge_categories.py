import os
import json
import glob

CATEGORIES_DIR = os.path.join(os.path.dirname(__file__), '../data/categories/')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '../data/trustlayer_plugin_data.json')

merged = []
for json_file in glob.glob(os.path.join(CATEGORIES_DIR, '*.json')):
    with open(json_file, 'r') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                merged.extend(data)
            else:
                print(f'[WARN] {json_file} does not contain a list, skipping.')
        except Exception as e:
            print(f'[ERROR] Failed to load {json_file}: {e}')

with open(OUTPUT_PATH, 'w') as out:
    json.dump(merged, out, indent=2)
print(f'[OK] Merged {len(merged)} entries into {OUTPUT_PATH}')
