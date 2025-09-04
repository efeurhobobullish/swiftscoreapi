from fastapi import FastAPI
import requests
from datetime import date, timedelta

app = FastAPI(title="SwiftScore API", version="1.0.0")

def format_match(m):
    return {
        "id": m.get("id"),
        "league": m.get("tournament", {}).get("name"),
        "home_team": m.get("homeTeam", {}).get("name"),
        "away_team": m.get("awayTeam", {}).get("name"),
        "home_logo": m.get("homeTeam", {}).get("logo"),
        "away_logo": m.get("awayTeam", {}).get("logo"),
        "home_score": m.get("homeScore", {}).get("current"),
        "away_score": m.get("awayScore", {}).get("current"),
        "status": m.get("status", {}).get("type"),
        "start_time": m.get("startTimestamp"),
    }

@app.get("/")
def root():
    return {"message": "SwiftScore Football API ⚽ is running!"}

@app.get("/matches/live")
def get_live_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    data = requests.get(url).json()
    return [format_match(m) for m in data.get("events", [])]

@app.get("/matches/upcoming")
def get_upcoming_matches():
    today = date.today().strftime("%Y-%m-%d")
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today}"
    data = requests.get(url).json()
    return [format_match(m) for m in data.get("events", [])]

@app.get("/matches/finished")
def get_finished_matches():
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{yesterday}"
    data = requests.get(url).json()
    return [format_match(m) for m in data.get("events", [])]

@app.get("/matches/all")
def get_all_matches():
    return {
        "live": get_live_matches(),
        "upcoming": get_upcoming_matches(),
        "finished": get_finished_matches()
    }
