import datetime
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow frontend (adjust origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fake browser headers to bypass 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.sofascore.com",
    "Origin": "https://www.sofascore.com",
}

def fetch_matches():
    """Fetch all matches for today from SofaScore and categorize them."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today}"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()

        live, upcoming, finished = [], [], []

        for event in data.get("events", []):
            match = {
                "id": event["id"],
                "tournament": event["tournament"]["name"],
                "homeTeam": event["homeTeam"]["name"],
                "awayTeam": event["awayTeam"]["name"],
                "homeScore": event["homeScore"].get("current"),
                "awayScore": event["awayScore"].get("current"),
                "status": event["status"]["description"],
                "startTime": datetime.datetime.fromtimestamp(event["startTimestamp"]).strftime("%Y-%m-%d %H:%M"),
            }

            # Categorize
            if event["status"]["type"] == "inprogress":
                live.append(match)
            elif event["status"]["type"] == "finished":
                finished.append(match)
            else:
                upcoming.append(match)

        return {"live": live, "upcoming": upcoming, "finished": finished}

    except Exception as e:
        return {"error": f"Failed to fetch data: {e}"}


@app.get("/api/matches")
def get_matches():
    """API endpoint to get today's matches separated into live, upcoming, and finished."""
    return fetch_matches()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
