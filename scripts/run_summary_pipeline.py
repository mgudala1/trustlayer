# scripts/run_summary_pipeline.py

from merge_scraped_data import merge_scraped_youtube_comments
from summarize_per_product import summarize_products, save_summary_to_json

def main():
    df = merge_scraped_youtube_comments()
    summaries = summarize_products(df)
    save_summary_to_json(summaries)

if __name__ == "__main__":
    main()
