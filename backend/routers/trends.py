from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
from models import SignalScore, Signal

router = APIRouter()

@router.get("/trends")
def get_trends(db: Session = Depends(get_db)):
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    # Get all brand+cluster combos
    combos = db.query(SignalScore.brand, SignalScore.cluster_id).distinct().all()
    results = []

    for brand, cluster_id in combos:
        # Current 7-day avg
        current = db.query(func.avg(SignalScore.hazra_score)).filter(
            SignalScore.brand == brand,
            SignalScore.cluster_id == cluster_id,
            SignalScore.date >= week_ago
        ).scalar() or 0

        # Previous 7-day avg
        previous = db.query(func.avg(SignalScore.hazra_score)).filter(
            SignalScore.brand == brand,
            SignalScore.cluster_id == cluster_id,
            SignalScore.date >= two_weeks_ago,
            SignalScore.date < week_ago
        ).scalar() or 0

        momentum = round(current - previous, 2)
        trend = "emerging" if momentum > 3 else ("declining" if momentum < -3 else "stable")

        # Daily scores for chart
        daily = db.query(SignalScore).filter(
            SignalScore.brand == brand,
            SignalScore.cluster_id == cluster_id,
            SignalScore.date >= now - timedelta(days=30)
        ).order_by(SignalScore.date).all()

        # Sample signals
        signals = db.query(Signal).filter(
            Signal.brand == brand,
            Signal.cluster_id == cluster_id
        ).limit(5).all()

        results.append({
            "brand": brand,
            "cluster_id": cluster_id,
            "cluster_label": cluster_id.replace("_", " ").title(),
            "momentum_score": momentum,
            "trend": trend,
            "current_avg": round(current, 2),
            "previous_avg": round(previous, 2),
            "daily_scores": [{"date": r.date.isoformat()[:10], "score": r.hazra_score} for r in daily],
            "signals": [{"content": s.content[:100], "type": s.type, "source": s.source} for s in signals],
        })

    results.sort(key=lambda x: abs(x["momentum_score"]), reverse=True)
    return results
