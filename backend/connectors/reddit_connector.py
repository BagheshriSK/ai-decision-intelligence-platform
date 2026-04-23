"""Reddit connector — uses public JSON API, no credentials needed."""
import httpx
from connectors.brand_detector import detect_brand, detect_cluster
from connectors.ingest_helper import ingest_signal

SUBREDDITS = ["samsung", "apple", "Android", "iphone", "GooglePixel"]
HEADERS = {"User-Agent": "DecisionIQ/1.0"}

def run_reddit():
    try:
        for sub in SUBREDDITS:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=50"
                response = httpx.get(url, headers=HEADERS, timeout=15)
                if response.status_code != 200:
                    print(f"Reddit r/{sub}: HTTP {response.status_code}")
                    continue
                posts = response.json().get("data", {}).get("children", [])
                for post in posts:
                    data = post.get("data", {})
                    text = f"{data.get('title', '')} {data.get('selftext', '')}".strip()
                    if not text:
                        continue
                    brand = detect_brand(text)
                    cluster = detect_cluster(text)
                    ingest_signal(
                        brand=brand,
                        cluster_id=cluster,
                        content=text[:1000],
                        source=f"reddit/r/{sub}",
                        sig_type="text"
                    )
            except Exception as e:
                print(f"Reddit r/{sub} error: {e}")
        print("Reddit connector: done.")
    except Exception as e:
        print(f"Reddit connector failed: {e}")
