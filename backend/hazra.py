"""HAZRA score computation: weighted composite of volume, velocity, sentiment, recency."""

WEIGHTS = {"volume": 0.25, "velocity": 0.30, "sentiment": 0.25, "recency": 0.20}

def compute_hazra(volume: float, velocity: float, sentiment: float, recency: float) -> float:
    """All inputs normalized 0-100. Returns weighted HAZRA score 0-100."""
    score = (
        WEIGHTS["volume"] * volume
        + WEIGHTS["velocity"] * velocity
        + WEIGHTS["sentiment"] * sentiment
        + WEIGHTS["recency"] * recency
    )
    return round(min(max(score, 0), 100), 2)

def normalize(value: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 50.0
    return round(((value - min_val) / (max_val - min_val)) * 100, 2)
