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
        if not data.get("response"):
            break
        players.extend(data["response"])
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


def fetch_player_stats_last_3_seasons(player_id, league_id=39, current_season=2023):
    seasons = [current_season, current_season-1, current_season-2]
    stats_list = []

    for season in seasons:
        url = "https://v3.football.api-sports.io/players"
        params = {"id": player_id, "league": league_id, "season": season}
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            continue

        data = response.json()
        if not data["response"]:
            continue

        stat = data["response"][0]["statistics"][0]
        stats_list.append({
            "season": season,
            "minutes": stat["games"].get("minutes", 0),
            "goals": stat["goals"].get("total", 0),
            "assists": stat["goals"].get("assists", 0),
            "position": stat["games"].get("position"),
            "tackles": stat["tackles"].get("total", 0),
            "interceptions": stat["tackles"].get("interceptions", 0),
            "clearances": stat["clearances"].get("total", 0),
            "blocks": stat.get("blocks", 0),
            "dribbles": stat["dribbles"].get("success", 0),
            "key_passes": stat["passes"].get("key", 0),
        })
    return pd.DataFrame(stats_list)
