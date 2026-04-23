"""Groq SDK wrapper with rate limiting (20 req/min) and exponential backoff retry."""
import os
import time
import threading
from collections import deque
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# Rate limiter: max 20 requests per 60 seconds
_lock = threading.Lock()
_request_times: deque = deque()
MAX_REQUESTS_PER_MINUTE = 20

def _wait_for_rate_limit():
    with _lock:
        now = time.time()
        # Remove timestamps older than 60 seconds
        while _request_times and now - _request_times[0] > 60:
            _request_times.popleft()
        # If at limit, wait until oldest request expires
        if len(_request_times) >= MAX_REQUESTS_PER_MINUTE:
            wait = 60 - (now - _request_times[0]) + 0.1
            if wait > 0:
                time.sleep(wait)
            # Clean up again after waiting
            now = time.time()
            while _request_times and now - _request_times[0] > 60:
                _request_times.popleft()
        _request_times.append(time.time())

def call_claude(prompt: str, max_tokens: int = 500) -> str:
    """Rate-limited Groq call with exponential backoff on 429."""
    _wait_for_rate_limit()

    max_retries = 3
    backoff = 2  # seconds

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower():
                wait = backoff * (2 ** attempt)
                print(f"LLM rate limit hit, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                print(f"LLM error: {e}")
                break

    return "Narrative unavailable — rate limit exceeded. Please try again shortly."
