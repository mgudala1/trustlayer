# scripts/load_keywords.py

import pandas as pd
import os

def load_all_keywords():
    # Automatically calculate the absolute path to the CSV files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")

    filenames = [
        "cpg_search_keywords_database.csv",
        "cpg_research_behavior_analysis.csv",
        "cpg_products_research_keywords.csv"
    ]

    all_keywords = set()
    skipped_keywords = []

    for filename in filenames:
        file_path = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(file_path)
            for col in df.columns:
                for keyword in df[col].dropna().astype(str).str.strip():
                    # Skip placeholders like [brand A], [category], etc.
                    if "[" in keyword or "]" in keyword:
                        skipped_keywords.append(keyword)
                        continue
                    all_keywords.add(keyword)
        except Exception as e:
            print(f"⚠️ Could not load {file_path}: {e}")

    # Optional: Log skipped template-style keywords
    if skipped_keywords:
        print(f"⚠️ Skipped {len(skipped_keywords)} placeholder keywords")

    return sorted(all_keywords)
