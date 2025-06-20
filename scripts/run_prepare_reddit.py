import os
from reddit_prepare_for_summary import process_reddit_threads

def main():
    # Get the absolute path to the root of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Correctly resolve the input and output file paths
    input_path = os.path.join(base_dir, "data", "reddit_cpg_sentiment_threads.json")
    output_path = os.path.join(base_dir, "data", "reddit_cpg_sentiment_threads_summary_ready.json")

    # Run the transformation
    process_reddit_threads(input_path, output_path)

if __name__ == "__main__":
    main()
