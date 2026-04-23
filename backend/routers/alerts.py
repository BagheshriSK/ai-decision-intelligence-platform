from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Alert

router = APIRouter()

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(desc(Alert.fired_at)).limit(50).all()
    return [
        {
            "id": a.id,
            "fired_at": a.fired_at.isoformat(),
            "cluster_id": a.cluster_id,
            "brand": a.brand,
            "hazra_score": a.hazra_score,
            "delta_24h": a.delta_24h,
            "recommended_action": a.recommended_action,
        }
        for a in alerts
    ]
