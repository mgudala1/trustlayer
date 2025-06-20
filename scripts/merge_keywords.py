# scripts/merge_keywords.py

import pandas as pd
import os

def load_merged_keywords():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")

    # Files
    search_csv = os.path.join(data_dir, "cpg_search_keywords_database.csv")
    behavior_csv = os.path.join(data_dir, "cpg_research_behavior_analysis.csv")
    product_csv = os.path.join(data_dir, "cpg_products_research_keywords.csv")  # optional if distinct

    all_keywords = set()
    skipped = []

    def split_keywords(col):
        return [kw.strip(" '\"") for kw in str(col).split(",") if "[" not in kw and "]" not in kw]

    try:
        # 1. Product/brand-specific search terms
        df1 = pd.read_csv(search_csv)
        for col in df1.columns:
            if col.lower().endswith("keywords"):
                for kw in df1[col].dropna():
                    all_keywords.update(split_keywords(kw))
    except Exception as e:
        print(f"⚠️ Could not load search_keywords_database.csv: {e}")

    try:
        # 2. Research behavior + drivers
        df2 = pd.read_csv(behavior_csv)
        for kwlist in df2["Keyword Types"].dropna():
            all_keywords.update(split_keywords(kwlist))
    except Exception as e:
        print(f"⚠️ Could not load behavior_analysis.csv: {e}")

    try:
        # 3. Optional product-research keywords
        df3 = pd.read_csv(product_csv)
        for col in df3.columns:
            for kw in df3[col].dropna():
                all_keywords.update(split_keywords(kw))
    except Exception as e:
        print(f"⚠️ Could not load products_research_keywords.csv: {e}")

    # Cleanup
    final_keywords = sorted(set(kw for kw in all_keywords if len(kw) > 2))
    print(f"✅ Merged total: {len(final_keywords)} search terms")

    return final_keywords
