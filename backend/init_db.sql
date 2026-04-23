-- Run this once to set up the database
-- Usage: psql -U postgres -f init_db.sql

CREATE DATABASE decisioniq;

\c decisioniq

CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    brand VARCHAR,
    cluster_id VARCHAR,
    cluster_label VARCHAR,
    date TIMESTAMP DEFAULT NOW(),
    type VARCHAR,
    content TEXT,
    embedding_id VARCHAR,
    source VARCHAR
);

CREATE TABLE IF NOT EXISTS signal_scores (
    id SERIAL PRIMARY KEY,
    brand VARCHAR,
    cluster_id VARCHAR,
    date TIMESTAMP,
    hazra_score FLOAT,
    volume FLOAT,
    velocity FLOAT,
    sentiment FLOAT,
    recency FLOAT
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    fired_at TIMESTAMP DEFAULT NOW(),
    cluster_id VARCHAR,
    brand VARCHAR,
    hazra_score FLOAT,
    delta_24h FLOAT,
    recommended_action TEXT
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR,
    role VARCHAR,
    message TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    brand VARCHAR,
    generated_at TIMESTAMP DEFAULT NOW(),
    content_markdown TEXT
);

CREATE TABLE IF NOT EXISTS config (
    key VARCHAR PRIMARY KEY,
    value VARCHAR
);

INSERT INTO config (key, value) VALUES ('threshold', '75') ON CONFLICT DO NOTHING;
