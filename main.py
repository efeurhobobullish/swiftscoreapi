# main.py
from fastapi import FastAPI
import requests
from datetime import date, timedelta

app = FastAPI(
    title="SwiftScore API",
    description="Get live, upcoming, and finished football matches from SofaScore",
    version="1.0.0"
)

BASE_URL = "https://api.sofascore.com/api/v1/sport/football"

def format_match(match: dict) -> dict:
    """Format a single match into clean JSON."""
    return {
        "id": match.get("id"),
        "tournament": match.get("tournament", {}).get("name"),
        "home": match.get("homeTeam", {}).get("name"),
        "away": match.get("awayTeam", {}).get("name"),
        "status": match.get("status", {}).get("description"),
        "startTime": match.get("startTimestamp"),
        "score": {
            "home": match.get("homeScore", {}).get("current"),
            "away": match.get("awayScore", {}).get("current"),
        }
    }

@app.get("/matches")
def get_matches(days: int = 3):
    """
    Fetch live, upcoming, and finished matches.
    - days: how many days forward/backward to fetch (default 3).
    """
    results = {"live": [], "upcoming": [], "finished": []}

    # 🔴 LIVE MATCHES
    try:
        live_url = f"{BASE_URL}/events/live"
        live_data = requests.get(live_url).json()
        results["live"] = [format_match(m) for m in live_data.get("events", [])]
    except Exception as e:
        print("Error fetching live matches:", e)

    # 🔵 UPCOMING MATCHES (today + next N days)
    for i in range(0, days):
        try:
            day = (date.today() + timedelta(days=i)).strftime("%Y-%m-%d")
            url = f"{BASE_URL}/scheduled-events/{day}"
            data = requests.get(url).json()
            results["upcoming"].extend([format_match(m) for m in data.get("events", [])])
        except Exception as e:
            print(f"Error fetching upcoming matches for {day}:", e)

    # 🟢 FINISHED MATCHES (yesterday - N days)
    for i in range(1, days + 1):
        try:
            day = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            url = f"{BASE_URL}/scheduled-events/{day}"
            data = requests.get(url).json()
            results["finished"].extend([format_match(m) for m in data.get("events", [])])
        except Exception as e:
            print(f"Error fetching finished matches for {day}:", e)

    return results
