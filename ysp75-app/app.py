import streamlit as st
import os
import pandas as pd
import requests

# הגדרת עמוד
st.set_page_config(page_title="FstarVfootball עם חיבור API", layout="wide")

API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {"x-apisports-key": API_KEY}

@st.cache_data
def load_data():
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_club_data():
    path = os.path.join("ysp75-app", "Updated_Club_Tactical_Dataset.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

def fetch_player_stats_from_api(player_id, league_id=39, season=2023):
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

# תחליף את זה בקוד שלך או השאר אם תרצה
def calculate_fit_score(player_row, club_row):
    # TODO: להכניס כאן את פונקציית ההתאמה המלאה שלך
    pass

def match_text(query, text):
    return query.lower() in str(text).lower()

def run_player_search():
    st.title("FstarVfootball")

    df = load_data()
    clubs_df = load_club_data()

    player_query = st.text_input("הקלד שם שחקן (חלק מהשם):", key="player_input").strip().lower()
    matching_players = df[df["Player"].apply(lambda name: match_text(player_query, name))]

    if player_query and not matching_players.empty:
        if len(matching_players) == 1:
            selected_player = matching_players["Player"].iloc[0]
        else:
            selected_player = st.selectbox("בחר שחקן מתוך תוצאות החיפוש:", matching_players["Player"].tolist())

        player_row = df[df["Player"] == selected_player].iloc[0]

        player_id_api = player_row.get("Player_ID_API", None)
        league_id = 39  # לדוגמה, פרמייר ליג
        season = 2023

        ysp_score = None

        if player_id_api:
            stats = fetch_player_stats_from_api(player_id_api, league_id, season)
            if stats:
                position = stats["games"]["position"] or player_row["Pos"]
                minutes = stats["games"]["minutes"] or 0
                goals = stats["goals"]["total"] or 0
                assists = stats["goals"]["assists"] or 0
                dribbles = stats.get("dribbles", {}).get("success", 0)
                key_passes = stats.get("passes", {}).get("key", 0)
                tackles = stats.get("tackles", {}).get("total", 0)
                interceptions = stats.get("tackles", {}).get("interceptions", 0)
                clearances = stats.get("clearances", {}).get("total", 0)
                blocks = stats.get("blocks", 0) if "blocks" in stats else 0
                age = player_row["Age"]
                league_name = "eng premier league"

                ysp_score = calculate_ysp_score_from_data(position, minutes, goals, assists, dribbles,
                                                         key_passes, tackles, interceptions, clearances,
                                                         blocks, age, league_name)

        if ysp_score is None:
            ysp_score = calculate_ysp_score_from_data(
                player_row["Pos"],
                player_row["Min"],
                player_row["Gls"],
                player_row["Ast"],
                player_row["Succ"],
                player_row["KP"],
                player_row["Tkl"],
                player_row["Int"],
                player_row["Clr"],
                player_row["Blocks"],
                player_row["Age"],
                player_row["Comp"]
            )

        st.metric("מדד YSP", ysp_score)

        st.subheader(f"שחקן: {player_row['Player']}")
        st.write(f"ליגה: {player_row['Comp']} | גיל: {player_row['Age']} | עמדה: {player_row['Pos']}")
        st.write(f"דקות: {player_row['Min']} | גולים: {player_row['Gls']} | בישולים: {player_row['Ast']}")
        st.write(f"דריבלים מוצלחים: {player_row['Succ']} | מסירות מפתח: {player_row['KP']}")

        club_query = st.text_input("הקלד שם קבוצה (חלק מהשם):", key="club_input").strip().lower()
        matching_clubs = [c for c in clubs_df["Club"].unique() if match_text(club_query, c)]

        if club_query and matching_clubs:
            selected_club = st.selectbox("בחר קבוצה מתוך התוצאות:", matching_clubs)
            club_data = clubs_df[clubs_df["Club"] == selected_club]
            if not club_data.empty:
                club_row = club_data.iloc[0]
                fit_score = calculate_fit_score(player_row=player_row, club_row=club_row)
                st.metric("רמת התאמה חזויה לקבוצה", f"{fit_score}%")
                if fit_score >= 85:
                    st.success("התאמה מצוינת – סביר שיצליח במערכת הזו.")
                elif fit_score >= 70:
                    st.info("התאמה סבירה – עשוי להסתגל היטב.")
                else:
                    st.warning("התאמה נמוכה – דרושה התאמה טקטית או סבלנות.")
        elif club_query:
            st.warning("לא נמצאו קבוצות תואמות.")
    else:
        if player_query:
            st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

    st.caption("הנתונים מבוססים על ניתוח אלגוריתמי לצרכים חינוכיים ואנליטיים בלבד.")

# כאן תוכל להוסיף פונקציות נוספות שלך כמו ניתוח תחזיות, היסטוריית חיפושים וכו'.

# תפריט בחירת מצב
mode = st.sidebar.radio("בחר מצב:", ("חיפוש שחקנים", "ניתוח תחזיות", "היסטוריית חיפושים"))

if mode == "חיפוש שחקנים":
    run_player_search()
elif mode == "ניתוח תחזיות":
    # כאן תפעיל את פונקציית ניתוח התחזיות שלך
    pass
elif mode == "היסטוריית חיפושים":
    # כאן תפעיל את פונקציית היסטוריית החיפושים שלך
    pass
