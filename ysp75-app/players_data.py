import os
import requests
import pandas as pd

API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {"x-apisports-key": API_KEY}

def fetch_players_from_api(league_id=39, season=2023):
    url = "https://v3.football.api-sports.io/players"
    players = []
    page = 1

    while True:
        params = {"league": league_id, "season": season, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}")

        data = response.json()

        # עצור אם אין תוצאות
        if not data.get("response"):
            break

        players.extend(data["response"])

        # עצור אם הגענו לדף האחרון
        if page >= data["paging"]["total"]:
            break

        page += 1

    simplified_players = []
    for p in players:
        player = p["player"]
        stats = p["statistics"][0] if p["statistics"] else {}

        simplified_players.append({
            "Player": player.get("name"),
            "Age": player.get("age"),
            "Pos": stats.get("games", {}).get("position"),
            "Min": stats.get("games", {}).get("minutes", 0),
            "Gls": stats.get("goals", {}).get("total", 0),
            "Ast": stats.get("goals", {}).get("assists", 0),
            "Tkl": stats.get("tackles", {}).get("total", 0),
            "Int": stats.get("tackles", {}).get("interceptions", 0),
            "Clr": stats.get("clearances", {}).get("total", 0),
            "Blocks": stats.get("blocks", 0),
            "Succ": stats.get("dribbles", {}).get("success", 0),
            "KP": stats.get("passes", {}).get("key", 0),
            "Comp": stats.get("league", {}).get("name"),
            "Player_ID_API": player.get("id"),
        })

    return pd.DataFrame(simplified_players)
