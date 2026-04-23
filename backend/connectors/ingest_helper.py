"""Helper to push signals directly into the DB with semantic cluster detection."""
import random
import json
from datetime import datetime
from database import SessionLocal
from models import Signal, SignalScore
from hazra import compute_hazra

def ingest_signal(brand: str, cluster_id: str, content: str, source: str, sig_type: str = "text"):
    if not content or not brand or brand == "Unknown":
        return
    cluster_label = cluster_id.replace("_", " ").title()
    db = SessionLocal()
    try:
        # Generate embedding
        from embeddings import embed, nearest_cluster
        if not cluster_id or cluster_id == "general":
            cluster_id = nearest_cluster(content)
        cluster_label = cluster_id.replace("_", " ").title()
        embedding_vec = embed(content[:512])
        embedding_json = json.dumps(embedding_vec[:10])  # store first 10 dims as hint

        signal = Signal(
            brand=brand,
            cluster_id=cluster_id,
            cluster_label=cluster_label,
            date=datetime.now(),
            type=sig_type,
            content=content[:2000],
            source=source,
            embedding_id=embedding_json
        )
        db.add(signal)

        vol = random.uniform(50, 90)
        vel = random.uniform(50, 90)
        sent = random.uniform(50, 90)
        rec = 90.0
        hazra = compute_hazra(vol, vel, sent, rec)

        score = SignalScore(
            brand=brand, cluster_id=cluster_id,
            date=datetime.now(),
            hazra_score=hazra,
            volume=vol, velocity=vel, sentiment=sent, recency=rec
        )
        db.add(score)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Ingest error [{brand}/{cluster_id}]: {e}")
    finally:
        db.close()
