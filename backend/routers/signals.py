from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import Optional
from database import get_db
from models import SignalScore, Signal

router = APIRouter()

def hazra_color(score: float) -> str:
    if score >= 75: return "red"
    if score >= 50: return "amber"
    return "green"

@router.get("/signals/ranked")
def get_ranked_signals(
    cluster_id: Optional[str] = None,
    brand: Optional[str] = None,
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    cutoff = datetime.now() - timedelta(days=days)
    q = db.query(SignalScore).filter(SignalScore.date >= cutoff)
    if cluster_id:
        q = q.filter(SignalScore.cluster_id == cluster_id)
    if brand:
        q = q.filter(SignalScore.brand == brand)
    scores = q.order_by(desc(SignalScore.hazra_score)).limit(200).all()

    results = []
    for s in scores:
        # Fetch a matching signal for content preview
        sig = db.query(Signal).filter(
            Signal.brand == s.brand,
            Signal.cluster_id == s.cluster_id
        ).first()
        results.append({
            "id": s.id,
            "brand": s.brand,
            "cluster_id": s.cluster_id,
            "date": s.date.isoformat(),
            "hazra_score": s.hazra_score,
            "volume": s.volume,
            "velocity": s.velocity,
            "sentiment": s.sentiment,
            "recency": s.recency,
            "color": hazra_color(s.hazra_score),
            "content_preview": sig.content[:120] if sig else "",
            "source": sig.source if sig else "",
            "type": sig.type if sig else "text",
        })
    return results
