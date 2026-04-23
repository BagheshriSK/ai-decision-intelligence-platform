"""APScheduler setup — starts all connectors on a schedule."""
from apscheduler.schedulers.background import BackgroundScheduler
from connectors.reddit_connector import run_reddit
from connectors.youtube_connector import run_youtube
from connectors.appstore_connector import run_appstore
from connectors.gnews_connector import run_gnews

scheduler = BackgroundScheduler()

def start_scheduler():
    # Run once immediately on startup
    run_gnews()
    run_reddit()

    # Schedule recurring jobs
    scheduler.add_job(run_gnews, "interval", minutes=30, id="gnews")
    scheduler.add_job(run_reddit, "interval", hours=1, id="reddit")
    scheduler.add_job(run_youtube, "interval", hours=3, id="youtube")
    scheduler.add_job(run_appstore, "interval", hours=6, id="appstore")

    scheduler.start()
    print("Signal connectors scheduler started.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
