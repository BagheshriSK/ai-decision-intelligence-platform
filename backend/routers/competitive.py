from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
from database import get_db
from models import SignalScore

router = APIRouter()

def _inflection_label(direction: str, delta: float) -> str:
    if direction == "surge":
        return f"+{abs(delta):.1f} pt surge detected"
    return f"-{abs(delta):.1f} pt drop detected"

@router.get("/competitive")
def get_competitive(
    client: str = Query("Samsung"),
    competitors: str = Query("Apple,Google Pixel"),
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    all_brands = [client] + [c.strip() for c in competitors.split(",") if c.strip()]
    cutoff = datetime.now() - timedelta(days=days)

    brand_data = {}
    for brand in all_brands:
        rows = db.query(SignalScore).filter(
            SignalScore.brand == brand,
            SignalScore.date >= cutoff
        ).order_by(SignalScore.date).all()

        daily: dict = {}
        for r in rows:
            day = r.date.strftime("%Y-%m-%d")
            if day not in daily:
                daily[day] = []
            daily[day].append(r.hazra_score)

        daily_avg = [{"date": d, "score": round(sum(v)/len(v), 2)} for d, v in sorted(daily.items())]

        # Detect inflection points: 7-day delta > ±10 (no LLM call)
        inflections = []
        for i in range(7, len(daily_avg)):
            delta = daily_avg[i]["score"] - daily_avg[i-7]["score"]
            if abs(delta) > 10:
                direction = "surge" if delta > 0 else "drop"
                inflections.append({
                    "date": daily_avg[i]["date"],
                    "delta": round(delta, 2),
                    "direction": direction,
                    "label": _inflection_label(direction, delta)
                })

        brand_data[brand] = {"daily": daily_avg, "inflections": inflections}

    return {"brands": all_brands, "data": brand_data, "days": days}
