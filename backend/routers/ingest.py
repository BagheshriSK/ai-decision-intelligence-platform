from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Signal, SignalScore
from hazra import compute_hazra
import random

router = APIRouter()

class IngestPayload(BaseModel):
    source: str
    type: str  # text|image|video
    content: str
    brand: str
    cluster_id: str
    cluster_label: str = ""

@router.post("/ingest")
def ingest_signal(payload: IngestPayload, db: Session = Depends(get_db)):
    # Store signal
    signal = Signal(
        brand=payload.brand,
        cluster_id=payload.cluster_id,
        cluster_label=payload.cluster_label or payload.cluster_id.replace("_", " ").title(),
        date=datetime.now(),
        type=payload.type,
        content=payload.content,
        source=payload.source,
        embedding_id=f"emb_{payload.cluster_id}_{random.randint(1000,9999)}"
    )
    db.add(signal)

    # Compute a new HAZRA score entry for today
    vol = random.uniform(50, 90)
    vel = random.uniform(50, 90)
    sent = random.uniform(50, 90)
    rec = 90.0  # just ingested = max recency
    hazra = compute_hazra(vol, vel, sent, rec)

    score = SignalScore(
        brand=payload.brand,
        cluster_id=payload.cluster_id,
        date=datetime.now(),
        hazra_score=hazra,
        volume=vol, velocity=vel, sentiment=sent, recency=rec
    )
    db.add(score)
    db.commit()
    db.refresh(signal)
    return {"id": signal.id, "hazra_score": hazra, "embedding_id": signal.embedding_id}
