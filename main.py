from fastapi import FastAPI
import requests
import datetime

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

def get_url_data(url):
    """Fetch and parse JSON from a given URL"""
    try:
        r = requests.get(url)
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
            "score": event.get("homeScore", {}).get("current")
        },
        "away": {
            "name": event["awayTeam"]["name"],
            "logo": f"https://api.sofascore.app/api/v1/team/{event['awayTeam']['id']}/image",
            "score": event.get("awayScore", {}).get("current")
        }
    }

@app.get("/")
def root():
    return {"message": "⚽ SofaScore Football API is running!"}

@app.get("/tournaments")
def get_tournaments():
    """Return all tournaments"""
    return tournaments

@app.get("/matches/{tournament_id}")
def matches(tournament_id: int, season_id: int = None):
    """Return live, upcoming, finished matches for one tournament"""
    if not season_id:
        seasons = get_url_data(f"{BASE_URL}/tournament/{tournament_id}/seasons")
        if "seasons" not in seasons:
            return {"error": "No seasons found"}
        season_id = seasons["seasons"][0]["id"]

    url = f"{BASE_URL}/tournament/{tournament_id}/season/{season_id}/events"
    data = get_url_data(url)
    if "events" not in data:
        return {"live": [], "upcoming": [], "finished": []}

    events = [format_event(e) for e in data["events"]]

    live = [e for e in events if e["status"].lower() == "live"]
    finished = [e for e in events if e["status"].lower() in ["ended", "finished", "after penalties"]]
    upcoming = [e for e in events if e["status"].lower() in ["not started", "scheduled"]]

    return {
        "tournament_id": tournament_id,
        "live": live,
        "upcoming": upcoming,
        "finished": finished
    }

@app.get("/matches/all")
def matches_all():
    """Return matches for all tournaments"""
    all_matches = {}
    for t in tournaments:
        all_matches[t["name"]] = matches(t["id"])
    return all_matches
