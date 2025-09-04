import requests

url = "https://api.sofascore.com/api/v1/tournament/36/season/62978/events"  # Example: La Liga 24/25
res = requests.get(url)
print(res.status_code)
print(res.json())
