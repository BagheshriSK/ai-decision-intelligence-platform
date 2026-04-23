"""LangGraph Sentinel agent: ingest_signals → score_clusters → evaluate_thresholds → format_alert → dispatch"""
import asyncio
from typing import TypedDict, List, Optional
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from database import SessionLocal
from models import SignalScore, Alert, Config

class SentinelState(TypedDict):
    scores: List[dict]
    threshold: float
    triggered: List[dict]
    alerts: List[dict]

def ingest_signals(state: SentinelState) -> SentinelState:
    db: Session = SessionLocal()
    cutoff = datetime.now() - timedelta(hours=24)
    rows = db.query(SignalScore).filter(SignalScore.date >= cutoff).all()
    state["scores"] = [
        {"brand": r.brand, "cluster_id": r.cluster_id, "hazra_score": r.hazra_score,
         "date": r.date.isoformat(), "volume": r.volume, "velocity": r.velocity}
        for r in rows
    ]
    db.close()
    return state

def score_clusters(state: SentinelState) -> SentinelState:
    # Compute 24h delta per brand+cluster
    db: Session = SessionLocal()
    enriched = []
    for s in state["scores"]:
        prev_cutoff = datetime.now() - timedelta(hours=48)
        prev = db.query(SignalScore).filter(
            SignalScore.brand == s["brand"],
            SignalScore.cluster_id == s["cluster_id"],
            SignalScore.date >= prev_cutoff,
            SignalScore.date < datetime.now() - timedelta(hours=24)
        ).order_by(SignalScore.date.desc()).first()
        delta = s["hazra_score"] - (prev.hazra_score if prev else s["hazra_score"])
        s["delta_24h"] = round(delta, 2)
        enriched.append(s)
    db.close()
    state["scores"] = enriched
    return state

def evaluate_thresholds(state: SentinelState) -> SentinelState:
    threshold = state.get("threshold", 75.0)
    state["triggered"] = [s for s in state["scores"] if s["hazra_score"] >= threshold]
    return state

def format_alert(state: SentinelState) -> SentinelState:
    alerts = []
    for t in state["triggered"]:
        direction = "surging" if t.get("delta_24h", 0) > 0 else "declining"
        action = (
            f"HAZRA score {t['hazra_score']:.1f} ({direction} {abs(t.get('delta_24h', 0)):.1f} pts). "
            f"Review {t['cluster_id']} signals for {t['brand']} and brief the marketing team immediately."
        )
        alerts.append({**t, "recommended_action": action, "fired_at": datetime.now().isoformat()})
    state["alerts"] = alerts
    return state

def dispatch(state: SentinelState) -> SentinelState:
    if not state["alerts"]:
        return state
    db: Session = SessionLocal()
    for a in state["alerts"]:
        # Avoid duplicate alerts within 1 hour
        recent = db.query(Alert).filter(
            Alert.cluster_id == a["cluster_id"],
            Alert.brand == a["brand"],
            Alert.fired_at >= datetime.now() - timedelta(hours=1)
        ).first()
        if not recent:
            db.add(Alert(
                cluster_id=a["cluster_id"],
                brand=a["brand"],
                hazra_score=a["hazra_score"],
                delta_24h=a.get("delta_24h", 0),
                recommended_action=a["recommended_action"]
            ))
    db.commit()
    db.close()
    return state

def build_sentinel_graph():
    graph = StateGraph(SentinelState)
    graph.add_node("ingest_signals", ingest_signals)
    graph.add_node("score_clusters", score_clusters)
    graph.add_node("evaluate_thresholds", evaluate_thresholds)
    graph.add_node("format_alert", format_alert)
    graph.add_node("dispatch", dispatch)
    graph.set_entry_point("ingest_signals")
    graph.add_edge("ingest_signals", "score_clusters")
    graph.add_edge("score_clusters", "evaluate_thresholds")
    graph.add_edge("evaluate_thresholds", "format_alert")
    graph.add_edge("format_alert", "dispatch")
    graph.add_edge("dispatch", END)
    return graph.compile()

sentinel_graph = build_sentinel_graph()

async def run_sentinel_loop():
    """Polls every 60 seconds."""
    while True:
        try:
            db: Session = SessionLocal()
            cfg = db.query(Config).filter_by(key="threshold").first()
            threshold = float(cfg.value) if cfg else 75.0
            db.close()
            sentinel_graph.invoke({"scores": [], "threshold": threshold, "triggered": [], "alerts": []})
        except Exception as e:
            print(f"Sentinel error: {e}")
        await asyncio.sleep(60)
