from fastapi import FastAPI
import requests
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

BASE_URL = "https://api.sofascore.com/api/v1"

# Predefined tournaments
tournaments = [
    {"name": "Champions League", "id": 1462},
    {"name": "Europa League", "id": 10908},
    {"name": "Premier League", "id": 1},
    {"name": "Bundesliga", "id": 42},
    {"name": "Brasileirão", "id": 83},
    {"name": "La Liga", "id": 36},
    {"name": "Serie A Tim", "id": 33},
    {"name": "Championship", "id": 2},
]

# Cache for daily refresh
cache = {"matches": {}}


def get_url_data(url):
    """Fetch and parse JSON from SofaScore"""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("❌ Error:", e)
    return {}


def format_event(event):
    """Simplify SofaScore event data"""
    return {
        "id": event.get("id"),
        "tournament": event.get("tournament", {}).get("name"),
        "start": datetime.datetime.fromtimestamp(
            event["startTimestamp"]
        ).strftime("%Y-%m-%d %H:%M"),
        "status": event["status"]["description"],
        "home": {
            "name": event["homeTeam"]["name"],
            "logo": f"https://api.sofascore.app/api/v1/team/{event['homeTeam']['id']}/image",
            "score": event.get("homeScore", {}).get("current"),
        },
        "away": {
            "name": event["awayTeam"]["name"],
            "logo": f"https://api.sofascore.app/api/v1/team/{event['awayTeam']['id']}/image",
            "score": event.get("awayScore", {}).get("current"),
        },
    }


def fetch_matches(tournament_id):
    """Fetch matches for one tournament"""
    seasons = get_url_data(f"{BASE_URL}/tournament/{tournament_id}/seasons")
    if "seasons" not in seasons or not seasons["seasons"]:
        return {"live": [], "upcoming": [], "finished": []}

    season_id = seasons["seasons"][0]["id"]
    url = f"{BASE_URL}/tournament/{tournament_id}/season/{season_id}/events"
    data = get_url_data(url)

    if "events" not in data:
        return {"live": [], "upcoming": [], "finished": []}

    events = [format_event(e) for e in data["events"]]

    live = [e for e in events if e["status"].lower() == "live"]
    finished = [e for e in events if e["status"].lower() in ["ended", "finished", "after penalties"]]
    upcoming = [e for e in events if e["status"].lower() in ["not started", "scheduled"]]

    return {"live": live, "upcoming": upcoming, "finished": finished}


def refresh_all_matches():
    """Update cache for all tournaments"""
    print("🔄 Refreshing matches from SofaScore...")
    all_matches = {}
    for t in tournaments:
        all_matches[t["name"]] = fetch_matches(t["id"])
    cache["matches"] = all_matches
    print("✅ Cache updated!")


# --- Scheduler: run every day at 06:00 ---
scheduler = BackgroundScheduler()
scheduler.add_job(refresh_all_matches, "cron", hour=6, minute=0)
scheduler.start()

# Run once at startup
refresh_all_matches()


@app.get("/")
def root():
    return {"message": "⚽ SofaScore Football API is running!"}


@app.get("/tournaments")
def get_tournaments():
    return tournaments


@app.get("/matches/{tournament_id}")
def matches(tournament_id: int):
    """Get matches for one tournament"""
    return fetch_matches(tournament_id)


@app.get("/matches/all")
def matches_all():
    """Get matches for all tournaments (from cache)"""
    return cache["matches"]
