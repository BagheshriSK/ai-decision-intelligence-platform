"""Seed 90 days of HAZRA scores, signals, and spike events."""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Signal, SignalScore, Alert, Config
from hazra import compute_hazra

BRANDS = ["BrandAlpha", "BrandBeta", "BrandGamma"]
CLUSTERS = {
    "wellness_trends": "Wellness Trends",
    "product_sentiment": "Product Sentiment",
    "competitor_mentions": "Competitor Mentions",
}
SOURCES = ["twitter", "reddit", "instagram", "news", "review_site"]
SPIKE_DAYS = [20, 55]  # days from start that have spikes

TEXT_TEMPLATES = [
    "Consumers are increasingly interested in {brand}'s new wellness line.",
    "Social buzz around {brand} products has surged this week.",
    "{brand} competitor mentions spiked after the latest campaign.",
    "Positive sentiment detected for {brand} in the {cluster} cluster.",
    "Users report high satisfaction with {brand} offerings.",
    "{brand} trending on social media for {cluster}.",
    "Negative reviews for {brand} decreased significantly.",
    "Influencers promoting {brand} products in wellness space.",
    "{brand} mentioned in 500+ posts related to {cluster}.",
    "Market analysts note {brand} momentum in {cluster} segment.",
]

def seed():
    init_db()
    db: Session = SessionLocal()

    # Check if already seeded
    seeded = db.query(Config).filter_by(key="seeded").first()
    if seeded:
        print("Already seeded.")
        db.close()
        return

    random.seed(42)
    start_date = datetime.now() - timedelta(days=90)

    # Seed config - use merge/upsert pattern for Postgres
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    stmt = pg_insert(Config).values([
        {"key": "threshold", "value": "75"},
        {"key": "seeded", "value": "true"}
    ]).on_conflict_do_nothing(index_elements=["key"])
    db.execute(stmt)

    # Seed signal scores (90 days per brand per cluster)
    for brand in BRANDS:
        for cluster_id, cluster_label in CLUSTERS.items():
            base_score = random.uniform(40, 65)
            for day in range(90):
                date = start_date + timedelta(days=day)
                # Add spike events for BrandAlpha
                is_spike = brand == "BrandAlpha" and any(abs(day - s) <= 1 for s in SPIKE_DAYS)
                if is_spike:
                    vol = random.uniform(80, 95)
                    vel = random.uniform(82, 92)
                    sent = random.uniform(78, 90)
                    rec = random.uniform(85, 95)
                else:
                    drift = random.uniform(-3, 3)
                    base_score = max(20, min(72, base_score + drift))
                    vol = max(0, min(100, base_score + random.uniform(-8, 8)))
                    vel = max(0, min(100, base_score + random.uniform(-8, 8)))
                    sent = max(0, min(100, base_score + random.uniform(-8, 8)))
                    rec = max(0, min(100, base_score + random.uniform(-8, 8)))

                hazra = compute_hazra(vol, vel, sent, rec)
                db.add(SignalScore(
                    brand=brand, cluster_id=cluster_id,
                    date=date, hazra_score=hazra,
                    volume=vol, velocity=vel, sentiment=sent, recency=rec
                ))

    # Seed 50 text signals + 10 image/video stubs per cluster for all brands
    for brand in BRANDS:
        for cluster_id, cluster_label in CLUSTERS.items():
            for i in range(50):
                tmpl = random.choice(TEXT_TEMPLATES)
                content = tmpl.format(brand=brand, cluster=cluster_label)
                db.add(Signal(
                    brand=brand, cluster_id=cluster_id,
                    cluster_label=cluster_label,
                    date=start_date + timedelta(days=random.randint(0, 89)),
                    type="text", content=content,
                    source=random.choice(SOURCES),
                    embedding_id=f"emb_{brand}_{cluster_id}_{i}"
                ))
            for i in range(10):
                sig_type = random.choice(["image", "video"])
                db.add(Signal(
                    brand=brand, cluster_id=cluster_id,
                    cluster_label=cluster_label,
                    date=start_date + timedelta(days=random.randint(0, 89)),
                    type=sig_type,
                    content=f"[{sig_type.upper()} stub] {cluster_label} asset #{i+1}",
                    source=random.choice(SOURCES),
                    embedding_id=f"emb_{sig_type}_{brand}_{cluster_id}_{i}"
                ))

    # Pre-fire 2 alerts for spike events
    for spike_day in SPIKE_DAYS:
        spike_date = start_date + timedelta(days=spike_day)
        db.add(Alert(
            fired_at=spike_date,
            cluster_id="wellness_trends",
            brand="BrandAlpha",
            hazra_score=random.uniform(85, 92),
            delta_24h=random.uniform(12, 18),
            recommended_action="Immediate review recommended: HAZRA spike detected. Engage marketing team to capitalize on momentum."
        ))

    db.commit()
    db.close()
    print("Seed complete.")

if __name__ == "__main__":
    seed()
