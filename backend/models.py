from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    cluster_id = Column(String, index=True)
    cluster_label = Column(String)
    date = Column(DateTime, default=func.now())
    type = Column(String)  # text|image|video
    content = Column(Text)
    embedding_id = Column(String, nullable=True)
    source = Column(String)

class SignalScore(Base):
    __tablename__ = "signal_scores"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    cluster_id = Column(String, index=True)
    date = Column(DateTime, index=True)
    hazra_score = Column(Float)
    volume = Column(Float)
    velocity = Column(Float)
    sentiment = Column(Float)
    recency = Column(Float)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    fired_at = Column(DateTime, default=func.now())
    cluster_id = Column(String)
    brand = Column(String)
    hazra_score = Column(Float)
    delta_24h = Column(Float)
    recommended_action = Column(Text)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=func.now())

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    generated_at = Column(DateTime, default=func.now())
    content_markdown = Column(Text)

class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True)
    value = Column(String)
