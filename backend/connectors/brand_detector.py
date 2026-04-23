"""Keyword-based brand and cluster detection."""

BRAND_KEYWORDS = {
    "Samsung": ["samsung", "galaxy s25", "galaxy", "samsung members"],
    "Apple": ["apple", "iphone 16", "iphone", "apple support", "ios"],
    "Google Pixel": ["google pixel", "pixel 9", "pixel", "google pixel 9"],
}

CLUSTER_KEYWORDS = {
    "camera": ["camera", "photo", "video", "lens", "zoom", "selfie", "shot", "picture"],
    "battery": ["battery", "charging", "charge", "power", "drain", "mah", "fast charge"],
    "overheating": ["overheat", "hot", "heat", "thermal", "temperature", "burning", "warm"],
    "price": ["price", "cost", "expensive", "cheap", "value", "worth", "afford", "dollar"],
    "performance": ["performance", "speed", "fast", "slow", "lag", "smooth", "processor", "ram", "benchmark"],
}

def detect_brand(text: str) -> str:
    text_lower = text.lower()
    for brand, keywords in BRAND_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return brand
    return "Unknown"

def detect_cluster(text: str) -> str:
    text_lower = text.lower()
    for cluster, keywords in CLUSTER_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return cluster
    return "general"
