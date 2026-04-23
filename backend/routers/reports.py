from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from database import get_db
from models import SignalScore, Alert, Report
from llm import call_claude

router = APIRouter()

@router.post("/reports/generate")
def generate_report(brand: str = Query("BrandAlpha"), db: Session = Depends(get_db)):
    cutoff = datetime.now() - timedelta(days=30)

    # Top clusters
    clusters = db.query(
        SignalScore.cluster_id,
        func.avg(SignalScore.hazra_score).label("avg_score"),
        func.count(SignalScore.id).label("count")
    ).filter(
        SignalScore.brand == brand,
        SignalScore.date >= cutoff
    ).group_by(SignalScore.cluster_id).order_by(desc("avg_score")).all()

    # Recent alerts
    alerts = db.query(Alert).filter(Alert.brand == brand).order_by(desc(Alert.fired_at)).limit(5).all()

    cluster_summary = "\n".join([
        f"- {c.cluster_id}: avg HAZRA={c.avg_score:.1f}, {c.count} data points"
        for c in clusters
    ])
    alert_summary = "\n".join([
        f"- {a.fired_at.strftime('%Y-%m-%d')}: score={a.hazra_score:.1f}, delta={a.delta_24h:+.1f}"
        for a in alerts
    ]) or "No recent alerts."

    prompt = f"""Generate a structured executive intelligence brief in markdown for brand '{brand}'.

Cluster Performance (last 30 days):
{cluster_summary}

Recent Alerts:
{alert_summary}

Include: Executive Summary, Key Findings per cluster, Risk Signals, Strategic Recommendations.
Use markdown headers, bullet points, and bold for key metrics."""

    markdown = call_claude(prompt, max_tokens=1000)

    report = Report(brand=brand, content_markdown=markdown)
    db.add(report)
    db.commit()
    db.refresh(report)

    return {"id": report.id, "brand": brand, "generated_at": report.generated_at.isoformat(), "content_markdown": markdown}

@router.get("/reports")
def list_reports(brand: str = Query("BrandAlpha"), db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.brand == brand).order_by(desc(Report.generated_at)).limit(10).all()
    return [{"id": r.id, "brand": r.brand, "generated_at": r.generated_at.isoformat(), "content_markdown": r.content_markdown} for r in reports]
