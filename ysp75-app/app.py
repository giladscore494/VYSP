import streamlit as st
import pandas as pd
from players_data import fetch_players_from_api, fetch_player_stats_last_3_seasons

st.set_page_config(page_title="FstarVfootball - 3 Seasons Stats", layout="wide")

# נוסחת חישוב YSP (כפי שהגדלת בקוד קודם, תתאים לפי הצורך)
def calculate_ysp_score_from_data(position, minutes, goals, assists, dribbles, key_passes,
                                 tackles, interceptions, clearances, blocks, age=25, league="eng premier league"):
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
    position = (position or "").upper()
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


def match_text(query, text):
    return query.lower() in str(text).lower()


def run_player_search():
    st.title("FstarVfootball - חיפוש שחקנים עם 3 עונות סטטיסטיקה")

    league_options = {
        "Premier League (eng)": 39,
        "La Liga (es)": 140,
        "Bundesliga (de)": 78,
        "Serie A (it)": 135,
        "Ligue 1 (fr)": 61
    }
    league_name = st.selectbox("בחר ליגה", options=list(league_options.keys()))
    league_id = league_options[league_name]

    season = st.number_input("בחר עונה נוכחית (לצפייה בשלוש עונות אחורה)", min_value=2019, max_value=2025, value=2023)

    with st.spinner("טוען נתונים מה-API..."):
        df = fetch_players_from_api(league_id=league_id, season=season)

    if df.empty:
        st.warning("לא נמצאו נתונים לשחקנים. נסה לבחור ליגה או עונה אחרת.")
        return

    player_query = st.text_input("הקלד שם שחקן (חלק מהשם):").strip().lower()
    matching_players = df[df["Player"].apply(lambda name: match_text(player_query, name))]

    if player_query and not matching_players.empty:
        if len(matching_players) == 1:
            selected_player = matching_players["Player"].iloc[0]
        else:
            selected_player = st.selectbox("בחר שחקן מתוך תוצאות החיפוש:", matching_players["Player"].tolist())

        player_row = df[df["Player"] == selected_player].iloc[0]

        st.subheader(f"שחקן: {player_row['Player']}")
        st.write(f"ליגה: {player_row['Comp']} | גיל: {player_row['Age']} | עמדה: {player_row['Pos']}")
        st.write(f"דקות: {player_row['Min']} | גולים: {player_row['Gls']} | בישולים: {player_row['Ast']}")
        st.write(f"דריבלים מוצלחים: {player_row['Succ']} | מסירות מפתח: {player_row['KP']}")

        # משיכת נתונים ל-3 עונות אחרונות לפי Player_ID_API
        player_id_api = player_row.get("Player_ID_API", None)
        if player_id_api:
            df_stats = fetch_player_stats_last_3_seasons(player_id_api, league_id, season)
            if not df_stats.empty:
                season_selected = st.selectbox("בחר עונה להצגה", options=df_stats["season"].tolist())
                selected_stats = df_stats[df_stats["season"] == season_selected].iloc[0]

                ysp = calculate_ysp_score_from_data(
                    selected_stats["position"],
                    selected_stats["minutes"],
                    selected_stats["goals"],
                    selected_stats["assists"],
                    selected_stats["dribbles"],
                    selected_stats["key_passes"],
                    selected_stats["tackles"],
                    selected_stats["interceptions"],
                    selected_stats["clearances"],
                    selected_stats["blocks"],
                    age=player_row["Age"],
                    league=player_row["Comp"]
                )

                st.write(f"---")
                st.write(f"**עונה:** {season_selected}")
                st.write(f"דקות: {selected_stats['minutes']}")
                st.write(f"גולים: {selected_stats['goals']}")
                st.write(f"בישולים: {selected_stats['assists']}")
                st.write(f"מדד YSP: {ysp}")

    else:
        if player_query:
            st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

    st.caption("הנתונים מבוססים על API-Football ועל מאגר טקטי מקומי.")


mode = st.sidebar.radio("בחר מצב:", ("חיפוש שחקנים",))

if mode == "חיפוש שחקנים":
    run_player_search()
