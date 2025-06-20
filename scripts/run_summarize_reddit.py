from summarize_reddit_per_product import load_reddit_data, summarize_reddit_by_product, save_to_json

def main():
    data = load_reddit_data()
    summaries = summarize_reddit_by_product(data)
    save_to_json(summaries)

if __name__ == "__main__":
    main()
