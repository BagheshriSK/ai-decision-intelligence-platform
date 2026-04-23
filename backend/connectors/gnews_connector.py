"""Google News connector — polls every 30 minutes."""
from connectors.brand_detector import detect_brand, detect_cluster
from connectors.ingest_helper import ingest_signal

QUERIES = ["Samsung Galaxy S25", "iPhone 16", "Google Pixel 9"]

def run_gnews():
    try:
        from gnews import GNews

        gnews = GNews(language="en", country="US", max_results=20)

        for query in QUERIES:
            try:
                articles = gnews.get_news(query)
                for article in articles:
                    title = article.get("title", "")
                    description = article.get("description", "")
                    content = f"{title}. {description}"
                    brand = detect_brand(content)
                    cluster = detect_cluster(content)
                    ingest_signal(
                        brand=brand,
                        cluster_id=cluster,
                        content=content[:1000],
                        source="google_news",
                        sig_type="text"
                    )
            except Exception as e:
                print(f"GNews query '{query}' error: {e}")

        print("GNews connector: done.")
    except Exception as e:
        print(f"GNews connector failed: {e}")
