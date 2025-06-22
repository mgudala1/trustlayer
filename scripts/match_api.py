from fastapi import FastAPI, HTTPException, Query
import json
from pathlib import Path
from rapidfuzz import fuzz  # Added import

app = FastAPI()
trust_data = []

@app.on_event("startup")
def load_data():
    global trust_data
    trust_data = []
    for file in Path("plugin/data/categories").glob("*.json"):
        with open(file) as f:
            trust_data.extend(json.load(f))
    print(f"[OK] Loaded {len(trust_data)} entries.")

@app.get("/match")
def match_product(title: str = Query(...)):
    normalized = title.lower().strip()
    best_entry = None
    best_score = 0

    for entry in trust_data:
        product_id = entry.get("product_id", "").lower()
        score = fuzz.token_set_ratio(normalized, product_id)
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_score >= 80:
        return best_entry
    raise HTTPException(status_code=404, detail="No match found")
