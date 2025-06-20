# scripts/youtube_search_and_scrape.py

from googleapiclient.discovery import build
from youtube_scraper import scrape_comments, save_comments
from merge_keywords import load_merged_keywords
import time

API_KEY = "AIzaSyA-x9jFSlzlDjkiB04A0jqF9LMY9yaSYQM"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_videos(query, max_results=5):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()

    videos = []
    for item in response.get("items", []):
        # ✅ Skip if there's no videoId
        if "videoId" not in item.get("id", {}):
            print(f"⚠️ Skipping item with no videoId: {item}")
            print("📦 ID payload:", item.get("id"))
            continue

        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append({
            "video_id": video_id,
            "title": title,
            "url": url
        })
    return videos

def main():
    keywords = load_merged_keywords()
    print(f"🔍 Loaded {len(keywords)} keywords")

    for idx, keyword in enumerate(keywords):
        if "," in keyword or len(keyword.split()) > 10:
            print(f"⚠️ Skipping malformed keyword: {keyword}")
            continue
        print(f"\n[{idx+1}/{len(keywords)}] 🔎 Searching for: {keyword}")
        videos = search_videos(keyword, max_results=3)

        for video in videos:
            print(f"📺 Scraping: {video['title']}")
            comments = scrape_comments(video['url'], max_comments=100)
            if comments:
                save_comments(video['video_id'], comments)
            time.sleep(1)  # avoid hitting rate limits

def test_main():
    # ✅ Test with a known good keyword
    keywords = ["CeraVe cleanser"]

    for idx, keyword in enumerate(keywords):
        print(f"\n[Test {idx+1}] 🔎 Searching for: {keyword}")
        videos = search_videos(keyword, max_results=1)

        for video in videos:
            print(f"📺 Scraping: {video['title']}")
            comments = scrape_comments(video['url'], max_comments=10)
            if comments:
                save_comments(video['video_id'], comments)

if __name__ == "__main__":
    # ✅ Toggle between test and full runs
    TEST_MODE = True

    if TEST_MODE:
        test_main()
    else:
        main()
