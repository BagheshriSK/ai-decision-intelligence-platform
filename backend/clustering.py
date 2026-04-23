"""HDBSCAN semantic clustering over signal embeddings."""
import numpy as np
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Signal, Config
from llm import call_claude

MIN_CLUSTER_SIZE = 50

def run_hdbscan_clustering():
    """Cluster all signals with embeddings. Label new clusters via LLM if >= 50 signals."""
    try:
        import hdbscan
    except ImportError:
        print("hdbscan not installed, skipping clustering.")
        return

    db: Session = SessionLocal()
    try:
        # Load signals that have embeddings stored as embedding_id (we use in-memory here)
        signals = db.query(Signal).filter(Signal.content != None).limit(2000).all()
        if len(signals) < MIN_CLUSTER_SIZE:
            return

        from embeddings import embed_batch
        texts = [s.content[:512] for s in signals]
        embeddings = embed_batch(texts)

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=5,
            metric="euclidean",
            cluster_selection_method="eom"
        )
        labels = clusterer.fit_predict(embeddings)

        # Find unique clusters (excluding noise = -1)
        unique_labels = set(labels) - {-1}

        for cluster_label in unique_labels:
            cluster_key = f"hdbscan_cluster_{cluster_label}"
            # Check if already labeled
            existing = db.query(Config).filter_by(key=cluster_key).first()
            if existing:
                continue

            # Get signals in this cluster
            indices = [i for i, l in enumerate(labels) if l == cluster_label]
            if len(indices) < MIN_CLUSTER_SIZE:
                continue

            # Sample up to 5 signals for LLM labeling
            sample_texts = [texts[i][:200] for i in indices[:5]]
            sample_str = "\n".join(f"- {t}" for t in sample_texts)

            prompt = (
                f"These consumer signals belong to the same semantic cluster:\n{sample_str}\n\n"
                "In 3 words or fewer, give this cluster a human-readable label (e.g. 'battery issues', 'camera quality')."
            )
            label = call_claude(prompt, max_tokens=20)
            label = label.strip().lower().replace(" ", "_")[:50]

            db.add(Config(key=cluster_key, value=label))
            db.commit()
            print(f"HDBSCAN: labeled cluster {cluster_label} as '{label}' ({len(indices)} signals)")

    except Exception as e:
        print(f"HDBSCAN clustering error: {e}")
    finally:
        db.close()
