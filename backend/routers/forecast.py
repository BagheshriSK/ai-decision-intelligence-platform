from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import SignalScore
from llm import call_claude
import pandas as pd
import numpy as np

router = APIRouter()

class ForecastRequest(BaseModel):
    cluster_id: str
    brand: str = "BrandAlpha"
    horizon_days: int = 7  # 7|14|28

def simple_forecast(scores: list, horizon: int):
    """Holt-Winters exponential smoothing fallback."""
    n = len(scores)
    alpha = 0.3  # smoothing factor
    # Double exponential smoothing
    s = [scores[0]]
    b = [scores[1] - scores[0] if n > 1 else 0]
    for i in range(1, n):
        s.append(alpha * scores[i] + (1 - alpha) * (s[-1] + b[-1]))
        b.append(0.1 * (s[-1] - s[-2]) + (1 - 0.1) * b[-1])
    last_s, last_b = s[-1], b[-1]
    preds = [last_s + (i + 1) * last_b for i in range(horizon)]
    # Confidence band: ±1 std of residuals
    residuals = [scores[i] - s[i] for i in range(n)]
    std = float(np.std(residuals)) if residuals else 5.0
    return preds, std

@router.post("/forecast")
def run_forecast(req: ForecastRequest, db: Session = Depends(get_db)):
    if req.horizon_days not in [7, 14, 28]:
        raise HTTPException(400, "horizon_days must be 7, 14, or 28")

    cutoff = datetime.now() - timedelta(days=90)
    rows = db.query(SignalScore).filter(
        SignalScore.brand == req.brand,
        SignalScore.cluster_id == req.cluster_id,
        SignalScore.date >= cutoff
    ).order_by(SignalScore.date).all()

    if len(rows) < 10:
        raise HTTPException(400, "Insufficient data for forecast")

    # Aggregate by day
    df = pd.DataFrame([{"ds": r.date.date(), "y": r.hazra_score} for r in rows])
    df = df.groupby("ds")["y"].mean().reset_index()
    scores = df["y"].tolist()
    dates = df["ds"].tolist()

    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        model = ExponentialSmoothing(scores, trend="add", seasonal=None, initialization_method="estimated")
        fit = model.fit(optimized=True)
        preds = fit.forecast(req.horizon_days).tolist()
        residuals = fit.resid.tolist()
        std = float(np.std(residuals))
    except Exception:
        preds, std = simple_forecast(scores, req.horizon_days)

    last_date = dates[-1]
    forecast_points = [
        {
            "date": (last_date + timedelta(days=i + 1)).strftime("%Y-%m-%d"),
            "yhat": round(min(max(preds[i], 0), 100), 2),
            "yhat_lower": round(min(max(preds[i] - 1.96 * std, 0), 100), 2),
            "yhat_upper": round(min(max(preds[i] + 1.96 * std, 0), 100), 2),
        }
        for i in range(req.horizon_days)
    ]

    historical = [
        {
            "date": str(dates[i]),
            "yhat": round(scores[i], 2),
            "yhat_lower": round(scores[i] - std, 2),
            "yhat_upper": round(scores[i] + std, 2),
        }
        for i in range(max(0, len(dates) - 30), len(dates))
    ]

    peak_row = max(forecast_points, key=lambda x: x["yhat"])
    peak_day = peak_row["date"]
    peak_score = peak_row["yhat"]

    prompt = (
        f"The HAZRA score forecast for cluster '{req.cluster_id}' (brand: {req.brand}) "
        f"over the next {req.horizon_days} days peaks at {peak_score:.1f} on {peak_day}. "
        "Write exactly 2 sentences of executive narrative summarizing the outlook and recommended action."
    )
    narrative = call_claude(prompt, max_tokens=150)

    return {
        "cluster_id": req.cluster_id,
        "brand": req.brand,
        "horizon_days": req.horizon_days,
        "peak_day": peak_day,
        "peak_score": peak_score,
        "narrative": narrative,
        "forecast": forecast_points,
        "historical": historical,
    }
