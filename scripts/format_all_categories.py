import os
import json
import glob
from jsonschema import validate, ValidationError

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '../trustlayer_plugin/data/product_feedback.schema.json')
CATEGORIES_DIR = os.path.join(os.path.dirname(__file__), '../trustlayer_plugin/data/categories/')

# Load schema
with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

for json_file in glob.glob(os.path.join(CATEGORIES_DIR, '*.json')):
    with open(json_file, 'r') as f:
        data = json.load(f)
    formatted = []
    for idx, entry in enumerate(data):
        formatted_entry = {
            'product_id': entry.get('product_id', ''),
            'source': entry.get('source', ''),
            'timestamp': entry.get('timestamp', ''),
            'feedback_text': entry.get('feedback_text', ''),
            'sentiment_label': entry.get('sentiment_label', ''),
            'authenticity_score': entry.get('authenticity_score', 0),
            'summary_text': entry.get('summary_text', ''),
            'metadata': entry.get('metadata', {}),
            'tags': entry.get('tags', [])
        }
        try:
            validate(instance=formatted_entry, schema=schema)
            formatted.append(formatted_entry)
        except ValidationError as ve:
            print(f'[SCHEMA ERROR] {json_file} [entry {idx}]: {ve.message}')
    with open(json_file, 'w') as out:
        json.dump(formatted, out, indent=2)
    print(f'[OK] Wrote {len(formatted)} valid entries to {json_file}')
