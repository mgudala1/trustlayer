from merge_platform_summaries import load_json, merge_summaries, save_combined_summary

def main():
    youtube = load_json("data/trustlayer_youtube_summary.json")
    reddit = load_json("data/trustlayer_reddit_summary.json")
    combined = merge_summaries(youtube, reddit)
    save_combined_summary(combined)

if __name__ == "__main__":
    main()
