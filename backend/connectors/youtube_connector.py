"""YouTube connector — polls every 3 hours."""
import os
from connectors.brand_detector import detect_brand, detect_cluster
from connectors.ingest_helper import ingest_signal

SEARCH_QUERIES = ["Samsung Galaxy S25 review", "iPhone 16 review", "Google Pixel 9 review"]

def run_youtube():
    try:
        api_key = os.getenv("YOUTUBE_API_KEY", "")
        if not api_key:
            print("YouTube: missing API key, skipping.")
            return

        from googleapiclient.discovery import build
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

        youtube = build("youtube", "v3", developerKey=api_key)

        for query in SEARCH_QUERIES:
            try:
                response = youtube.search().list(
                    q=query, part="snippet", type="video",
                    maxResults=10, order="date"
                ).execute()

                for item in response.get("items", []):
                    video_id = item["id"]["videoId"]
                    title = item["snippet"]["title"]
                    description = item["snippet"].get("description", "")

                    # Try to get transcript
                    transcript_text = ""
                    try:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        transcript_text = " ".join([t["text"] for t in transcript[:100]])
                    except (NoTranscriptFound, TranscriptsDisabled):
                        transcript_text = f"{title}. {description}"
                    except Exception:
                        transcript_text = f"{title}. {description}"

                    content = f"{title}. {transcript_text}"
                    brand = detect_brand(content)
                    cluster = detect_cluster(content)
                    ingest_signal(
                        brand=brand,
                        cluster_id=cluster,
                        content=content[:1500],
                        source=f"youtube/{video_id}",
                        sig_type="video"
                    )
            except Exception as e:
                print(f"YouTube query '{query}' error: {e}")

        print("YouTube connector: done.")
    except Exception as e:
        print(f"YouTube connector failed: {e}")
