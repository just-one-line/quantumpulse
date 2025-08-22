"""
fed_scanner.py
----------------
Lightweight scanner for upcoming Federal Reserve (FOMC) events + importance score.

It pulls from two public sources:
1) Fed press releases (Monetary Policy) RSS feed
2) FOMC calendar page (best‑effort scrape, with graceful fallback)

It returns a normalized list of events with:
- date (UTC), title, url, kind, importance score (0–100)

Dependencies (we’ll add them to requirements.txt in the next step):
requests, beautifulsoup4, feedparser, python-dateutil
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import feedparser  # RSS for press releases
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser


FED_RSS = "https://www.federalreserve.gov/feeds/press_monetary.xml"
FOMC_CAL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

# Heuristic keywords to estimate event importance.
KEYWORD_SCORES = {
    "fomc statement": 95,
    "press conference": 90,
    "summary of economic projections": 90,
    "policy statement": 90,
    "interest rate decision": 88,
    "minutes": 60,
    "chair powell remarks": 85,
    "press release": 55,
    "meeting": 50,
}

@dataclass
class Event:
    date: datetime
    title: str
    url: str
    kind: str  # "rss" or "calendar"
    importance: int

    def to_public(self) -> dict:
        d = asdict(self)
        # ISO 8601 string
        d["date"] = self.date.astimezone(timezone.utc).isoformat()
        return d


def _score_title(title: str) -> int:
    t = title.lower()
    score = 0
    for kw, s in KEYWORD_SCORES.items():
        if kw in t:
            score = max(score, s)
    # Small boost for explicit “FOMC”
    if "fomc" in t:
        score = max(score, 70)
    return score or 40  # default floor


def fetch_press_release_events(limit: int = 30) -> List[Event]:
    """Fetch recent Fed monetary policy press releases (RSS)."""
    events: List[Event] = []
    feed = feedparser.parse(FED_RSS)

    for entry in feed
