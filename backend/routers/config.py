from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Config

router = APIRouter()

class ThresholdUpdate(BaseModel):
    threshold: float

@router.patch("/config/threshold")
def update_threshold(body: ThresholdUpdate, db: Session = Depends(get_db)):
    cfg = db.query(Config).filter_by(key="threshold").first()
    if cfg:
        cfg.value = str(body.threshold)
    else:
        db.add(Config(key="threshold", value=str(body.threshold)))
    db.commit()
    return {"threshold": body.threshold}

@router.get("/config/threshold")
def get_threshold(db: Session = Depends(get_db)):
    cfg = db.query(Config).filter_by(key="threshold").first()
    return {"threshold": float(cfg.value) if cfg else 75.0}
