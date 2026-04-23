"""App Store connector — polls every 6 hours."""
from connectors.brand_detector import detect_brand, detect_cluster
from connectors.ingest_helper import ingest_signal

# (app_id, brand, app_name)
APPS = [
    ("1117786766", "Samsung", "Samsung Members"),
    ("1130498044", "Apple", "Apple Support"),
    ("1486571841", "Google Pixel", "Pixel Buds"),
]

def run_appstore():
    try:
        from app_store_scraper import AppStore

        for app_id, brand, app_name in APPS:
            try:
                app = AppStore(country="us", app_name=app_name, app_id=app_id)
                app.review(how_many=100)
                for review in app.reviews:
                    content = f"{review.get('title', '')}. {review.get('review', '')}"
                    cluster = detect_cluster(content)
                    ingest_signal(
                        brand=brand,
                        cluster_id=cluster,
                        content=content[:1000],
                        source=f"appstore/{app_name.lower().replace(' ', '_')}",
                        sig_type="text"
                    )
            except Exception as e:
                print(f"AppStore {app_name} error: {e}")

        print("AppStore connector: done.")
    except Exception as e:
        print(f"AppStore connector failed: {e}")
