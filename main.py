import requests
import datetime
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# 🎯 Supported tournaments (filter only these)
TOURNAMENTS = [
    {"name": "Champions League", "id": 1462},
    {"name": "Europa League", "id": 10908},
    {"name": "Premier League", "id": 1},
    {"name": "Bundesliga", "id": 42},
    {"name": "Brasileirão", "id": 83},
    {"name": "La Liga", "id": 36},
    {"name": "Serie A Tim", "id": 33},
    {"name": "Championship", "id": 2},
]

app = FastAPI()

def get_today_matches():
    today = datetime.date.today().strftime("%Y-%m-%d")
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today}"

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch data: {e}"}

    data = res.json()
    events = data.get("events", [])

    allowed_ids = {t["id"]: t["name"] for t in TOURNAMENTS}
    live, upcoming, finished = [], [], []

    for e in events:
        tournament_id = e["tournament"]["uniqueTournament"]["id"]
        if tournament_id not in allowed_ids:
            continue

        match = {
            "id": e["id"],
            "tournament": allowed_ids[tournament_id],
            "time": datetime.datetime.fromtimestamp(e["startTimestamp"]).strftime("%Y-%m-%d %H:%M"),
            "homeTeam": e["homeTeam"]["name"],
            "awayTeam": e["awayTeam"]["name"],
            "homeScore": e["homeScore"].get("current"),
            "awayScore": e["awayScore"].get("current"),
            "status": e["status"]["description"]
        }

        code = e["status"]["code"]
        if code == 100:  # finished
            finished.append(match)
        elif code == 0:  # upcoming
            upcoming.append(match)
        else:  # live
            live.append(match)

    return {"live": live, "upcoming": upcoming, "finished": finished}

# 🖥️ API endpoint
@app.get("/matches")
def matches():
    return JSONResponse(content=get_today_matches())

# 🖥️ Run as standalone script OR API
if __name__ == "__main__":
    # Run FastAPI app on localhost:8000
    print("🚀 Starting FastAPI server at http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # OR, to just print matches instead of running API, uncomment below:
    # print(json.dumps(get_today_matches(), indent=2, ensure_ascii=False))
