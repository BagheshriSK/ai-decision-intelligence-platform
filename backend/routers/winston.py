from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional
from database import get_db
from models import ChatSession, SignalScore, Signal
from llm import call_claude

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    context: Optional[dict] = {}

def build_rag_context(brand: Optional[str], cluster_id: Optional[str], query: str, db: Session) -> str:
    # Semantic similarity: find signals closest to the user's query
    try:
        from embeddings import embed
        import numpy as np
        query_vec = np.array(embed(query))

        sig_q = db.query(Signal)
        if brand:
            sig_q = sig_q.filter(Signal.brand == brand)
        if cluster_id:
            sig_q = sig_q.filter(Signal.cluster_id == cluster_id)
        candidates = sig_q.limit(200).all()

        # Score by cosine similarity using stored embedding hint (fallback to recency)
        scored = []
        for s in candidates:
            try:
                import json
                stored = json.loads(s.embedding_id or "[]")
                if len(stored) >= 10:
                    sim = float(np.dot(query_vec[:10], np.array(stored[:10])))
                    scored.append((sim, s))
                else:
                    scored.append((0.0, s))
            except Exception:
                scored.append((0.0, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        signals = [s for _, s in scored[:5]]
    except Exception:
        # Fallback to recency
        sig_q = db.query(Signal)
        if brand:
            sig_q = sig_q.filter(Signal.brand == brand)
        signals = sig_q.limit(5).all()

    q = db.query(SignalScore)
    if brand:
        q = q.filter(SignalScore.brand == brand)
    if cluster_id:
        q = q.filter(SignalScore.cluster_id == cluster_id)
    top_scores = q.order_by(desc(SignalScore.hazra_score)).limit(5).all()

    score_ctx = "\n".join([
        f"- {s.brand}/{s.cluster_id}: HAZRA={s.hazra_score:.1f} on {s.date.strftime('%Y-%m-%d')}"
        for s in top_scores
    ])
    signal_ctx = "\n".join([f"- [{s.type}] {s.content[:100]}" for s in signals])
    return f"Top HAZRA Scores:\n{score_ctx}\n\nSemantically Relevant Signals:\n{signal_ctx}"

@router.post("/winston/chat")
def winston_chat(req: ChatRequest, db: Session = Depends(get_db)):
    brand = req.context.get("brand") if req.context else None
    cluster_id = req.context.get("cluster_id") if req.context else None

    # Load session history (last 10 turns)
    history = db.query(ChatSession).filter(
        ChatSession.session_id == req.session_id
    ).order_by(ChatSession.timestamp).all()

    history_text = "\n".join([f"{h.role}: {h.message}" for h in history[-10:]])
    rag_ctx = build_rag_context(brand, cluster_id, db)

    prompt = f"""You are Winston, an AI decision intelligence assistant for consumer signal analysis.

Context data:
{rag_ctx}

Conversation history:
{history_text}

User: {req.message}

Answer concisely and reference the signal data where relevant. If asked to generate a report, produce structured markdown."""

    response = call_claude(prompt, max_tokens=600)

    # Persist messages
    db.add(ChatSession(session_id=req.session_id, role="user", message=req.message, timestamp=datetime.now()))
    db.add(ChatSession(session_id=req.session_id, role="assistant", message=response, timestamp=datetime.now()))
    db.commit()

    return {"response": response, "session_id": req.session_id}

@router.get("/winston/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    history = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).order_by(ChatSession.timestamp).all()
    return [{"role": h.role, "message": h.message, "timestamp": h.timestamp.isoformat()} for h in history]
