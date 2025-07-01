import streamlit as st
import os
import requests

st.set_page_config(page_title="FstarVfootball - API בלבד", layout="wide")

API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {"x-apisports-key": API_KEY}

# פונקציה לחיפוש שחקנים לפי שם חלקי
def search_players(name_query, league_id=39, season=2023):
    url = "https://v3.football.api-sports.io/players"
    players = []
    page = 1
    while True:
        params = {
            "search": name_query,
            "league": league_id,
            "season": season,
            "page": page
        }
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            st.error(f"שגיאה בחיפוש שחקנים: {response.status_code}")
            break
        data = response.json()
        if not data["response"]:
            break
        players.extend(data["response"])
        if page >= data["paging"]["total"]:
            break
        page += 1
    return players

# פונקציה לשליפת סטטיסטיקות של שחקן לפי מזהה
def fetch_player_stats(player_id, league_id=39, season=2023):
    url = "https://v3.football.api-sports.io/players"
    params = {"id": player_id, "league": league_id, "season": season}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        st.error(f"שגיאה בשליפת נתוני שחקן: {response.status_code}")
        return None
    data = response.json()
    if data["response"]:
        return data["response"][0]["statistics"][0]
    return None

# פונקציית חישוב מדד YSP מהנתונים
def calculate_ysp_score_from_data(position, minutes, goals, assists, dribbles, key_passes,
                                 tackles, interceptions, clearances, blocks, age, league):
    benchmarks = {
        "GK": {"Min": 3000, "Clr": 30, "Tkl": 10, "Blocks": 15},
        "DF": {"Tkl": 50, "Int": 50, "Clr": 120, "Blocks": 30, "Min": 3000, "Gls": 3, "Ast": 2},
        "MF": {"Gls": 10, "Ast": 10, "Succ": 50, "KP": 50, "Min": 3000},
        "FW": {"Gls": 20, "Ast": 15, "Succ": 40, "KP": 40, "Min": 3000}
    }

    league_weights = {
        "eng premier league": 1.00,
        "es la liga": 0.98,
        "de bundesliga": 0.96,
        "it serie a": 0.95,
        "fr ligue 1": 0.93
    }

    ysp_score = 0
    position = position.upper()
    if "GK" in position:
        bm = benchmarks["GK"]
        ysp_score = (
            (minutes / bm["Min"]) * 40 +
            (clearances / bm["Clr"]) * 20 +
            (tackles / bm["Tkl"]) * 20 +
            (blocks / bm["Blocks"]) * 20
        )
    elif "DF" in position:
        bm = benchmarks["DF"]
        ysp_score = (
            (tackles / bm["Tkl"]) * 18 +
            (interceptions / bm["Int"]) * 18 +
            (clearances / bm["Clr"]) * 18 +
            (blocks / bm["Blocks"]) * 10 +
            (minutes / bm["Min"]) * 10 +
            (goals / bm["Gls"]) * 13 +
            (assists / bm["Ast"]) * 13
        )
    elif "MF" in position:
        bm = benchmarks["MF"]
        ysp_score = (
            (goals / bm["Gls"]) * 20 +
            (assists / bm["Ast"]) * 20 +
            (dribbles / bm["Succ"]) * 20 +
            (key_passes / bm["KP"]) * 20 +
            (minutes / bm["Min"]) * 20
        )
    elif "FW" in position:
        bm = benchmarks["FW"]
        ysp_score = (
            (goals / bm["Gls"]) * 30 +
            (assists / bm["Ast"]) * 25 +
            (dribbles / bm["Succ"]) * 15 +
            (key_passes / bm["KP"]) * 15 +
            (minutes / bm["Min"]) * 15
        )
    else:
        ysp_score = (goals * 3 + assists * 2 + minutes / 250)

    if minutes > 0:
        contribution_per_90 = ((goals + assists + dribbles * 0.5 + key_passes * 0.5) / minutes) * 90
        if contribution_per_90 >= 1.2:
            ysp_score += 15
        elif contribution_per_90 >= 0.9:
            ysp_score += 10
        elif contribution_per_90 >= 0.6:
            ysp_score += 5

    if age <= 20:
        ysp_score *= 1.1
    elif age <= 23:
        ysp_score *= 1.05

    league_weight = league_weights.get(league.strip().lower(), 0.9)
    ysp_score *= league_weight
    return min(round(ysp_score, 2), 100)

league_map = {
    39: "eng premier league",
    140: "es la liga",
    78: "de bundesliga",
    135: "it serie a",
    61: "fr ligue 1"
}

st.title("FstarVfootball - מדד YSP מבוסס API בלבד")

league_id = st.selectbox("בחר ליגה", options=list(league_map.keys()), format_func=lambda x: league_map[x].title())
season = st.number_input("בחר עונה", min_value=2010, max_value=2025, value=2023)

name_query = st.text_input("הקלד שם שחקן (חלק מהשם):").strip()

if name_query:
    players = search_players(name_query, league_id=league_id, season=season)
    if not players:
        st.warning("לא נמצאו שחקנים התואמים את החיפוש.")
    else:
        player_names = [p["player"]["name"] for p in players]
        selected_name = st.selectbox("בחר שחקן:", player_names)
        selected_player = next(p for p in players if p["player"]["name"] == selected_name)
        player_id = selected_player["player"]["id"]

        stats = fetch_player_stats(player_id, league_id=league_id, season=season)

        if stats:
            position = stats["games"]["position"] or "Unknown"
            minutes = stats["games"]["minutes"] or 0
            goals = stats["goals"]["total"] or 0
            assists = stats["goals"]["assists"] or 0
            dribbles = stats.get("dribbles", {}).get("success", 0)
            key_passes = stats.get("passes", {}).get("key", 0)
            tackles = stats.get("tackles", {}).get("total", 0)
            interceptions = stats.get("tackles", {}).get("interceptions", 0)
            clearances = stats.get("clearances", {}).get("total", 0)
            blocks = stats.get("blocks", 0) if "blocks" in stats else 0
            age = selected_player["player"].get("age", 25) or 25
            league_name = league_map.get(league_id, "Unknown")

            ysp_score = calculate_ysp_score_from_data(position, minutes, goals, assists, dribbles, key_passes,
                                                     tackles, interceptions, clearances, blocks, age, league_name)

            st.subheader(f"שחקן: {selected_name}")
            st.write(f"ליגה: {league_name.title()} | גיל: {age} | עמדה: {position}")
            st.write(f"דקות: {minutes} | גולים: {goals} | בישולים: {assists}")
            st.write(f"דריבלים מוצלחים: {dribbles} | מסירות מפתח: {key_passes}")
            st.metric("מדד YSP", ysp_score)
        else:
            st.warning("אין נתונים זמינים לשחקן זה בעונה ובליגה הנבחרים.")
