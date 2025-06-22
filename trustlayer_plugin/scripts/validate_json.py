import os
import json
import glob
from jsonschema import validate, ValidationError

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '../data/product_feedback.schema.json')
CATEGORIES_DIR = os.path.join(os.path.dirname(__file__), '../data/categories/')

# Load schema
with open(SCHEMA_PATH, 'r') as f:
    schema = json.load(f)

# Validate each JSON file in categories
for json_file in glob.glob(os.path.join(CATEGORIES_DIR, '*.json')):
    with open(json_file, 'r') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f'[ERROR] Failed to load {json_file}: {e}')
            continue
    for idx, entry in enumerate(data):
        try:
            validate(instance=entry, schema=schema)
        except ValidationError as ve:
            print(f'[SCHEMA ERROR] {json_file} [entry {idx}]: {ve.message}')
        else:
            print(f'[OK] {json_file} [entry {idx}] is valid.')
