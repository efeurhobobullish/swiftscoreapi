from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI()

# Replace with your API key + endpoint
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://livescore-api.com/api-client/matches/live.json"

def fetch_matches():
    url = f"{BASE_URL}?key={API_KEY}"
    resp = requests.get(url)
    data = resp.json()

    if not data.get("success"):
        return {"live": [], "upcoming": [], "finished": []}

    matches = data.get("data", {}).get("match", [])

    live, upcoming, finished = [], [], []

    for m in matches:
        status = m.get("status", "").upper()

        match_data = {
            "id": m.get("id"),
            "home": m["home"]["name"],
            "away": m["away"]["name"],
            "score": m["scores"]["score"] if "scores" in m else None,
            "time": m.get("time"),
            "competition": m["competition"]["name"] if "competition" in m else None,
            "status": status,
            "home_logo": m["home"]["logo"],
            "away_logo": m["away"]["logo"]
        }

        if status in ["IN PLAY", "ADDED TIME", "1ST HALF", "2ND HALF"]:
            live.append(match_data)
        elif status == "FINISHED":
            finished.append(match_data)
        else:
            upcoming.append(match_data)

    return {"live": live, "upcoming": upcoming, "finished": finished}

@app.get("/matches")
def get_matches():
    return fetch_matches()
