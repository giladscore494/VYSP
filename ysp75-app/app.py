import streamlit as st
import os
import pandas as pd
from search_history import save_search, show_search_history
import urllib.parse

# הגדרת עמוד
st.set_page_config(page_title="FstarVfootball", layout="wide")

# טעינת CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

def match_text(query, text):
    return query.lower() in str(text).lower()

def generate_transfermarkt_link(player_name: str, club: str = "") -> str:
    base_url = "https://duckduckgo.com/"
    query = f"{player_name} {club} site:transfermarkt.com"
    encoded_query = urllib.parse.urlencode({"q": query})
    return f"{base_url}?{encoded_query}"

def calculate_minute_penalty(minutes, age):
    if minutes >= 1000:
        return 0
    elif age <= 20:
        return (1000 - minutes) / 1000 * 5
    elif age <= 23:
        return (1000 - minutes) / 1000 * 10
    else:
        return (1000 - minutes) / 1000 * 15

def calculate_fit_score(player_row, club_row):
    # (כפי שהיה קודם, לא שונה)
    ...

def predict_roi(current_value, predicted_value):
    if not current_value or current_value <= 0:
        return "N/A"
    roi = (predicted_value - current_value) / current_value * 100
    return round(roi, 1)

def calculate_ysp_score(row, market_value_eur=None):
    position = str(row["Pos"])
    minutes = row["Min"]
    goals = row["Gls"]
    assists = row["Ast"]
    dribbles = row["Succ"]
    key_passes = row["KP"]
    tackles = row["Tkl"]
    interceptions = row["Int"]
    clearances = row["Clr"]
    blocks = row["Blocks"]
    age = row["Age"]
    league = row["Comp"]

    benchmarks = {
        "GK": {"Min": 3000, "Clr": 30, "Tkl": 10, "Blocks": 15},
        "DF": {"Tkl": 50, "Int": 50, "Clr": 120, "Blocks": 30, "Min": 3000, "Gls": 3, "Ast": 2},
        "MF": {"Gls": 10, "Ast": 10, "Succ": 50, "KP": 50, "Min": 3000},
        "FW": {"Gls": 20, "Ast": 15, "Succ": 40, "KP": 40, "Min": 3000}
    }

    league_weights = {
        "eng Premier League": 1.00,
        "es La Liga": 0.98,
        "de Bundesliga": 0.96,
        "it Serie A": 0.95,
        "fr Ligue 1": 0.93
    }

    ysp_score = 0
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

    league_weight = league_weights.get(league.strip(), 0.9)
    ysp_score *= league_weight

    penalty = calculate_minute_penalty(minutes, age)
    ysp_score -= penalty

    if market_value_eur and market_value_eur > 0:
        market_boost = min(market_value_eur / 1000000, 30)
        ysp_score += market_boost

    return min(round(ysp_score, 2), 100)

def run_player_search():
    df = load_data()
    clubs_df = load_club_data()

    player_query = st.text_input("הקלד שם שחקן (חלק מהשם):", key="player_input").strip().lower()
    matching_players = df[df["Player"].apply(lambda name: match_text(player_query, name))]

    if player_query and not matching_players.empty:
        selected_player = st.selectbox("בחר שחקן מתוך התוצאות:", matching_players["Player"].tolist())
        row = df[df["Player"] == selected_player].iloc[0]

        st.subheader(f"סטטיסטיקת שחקן: {row['Player']}")
        st.write(f"גיל: {row['Age']} | עמדה: {row['Pos']} | דקות: {row['Min']}")
        st.write(f"גולים: {row['Gls']} | בישולים: {row['Ast']} | דריבלים: {row['Succ']} | מסירות מפתח: {row['KP']}")

        st.markdown("---")
        st.write("**הזן שווי שוק נוכחי (יורו):**")
        input_market_value = st.number_input("Market Value (EUR)", min_value=0, step=500000, format="%d")

        ysp_score = calculate_ysp_score(row, market_value_eur=input_market_value)
        st.metric("מדד YSP-75", ysp_score)

        if input_market_value and input_market_value > 0:
            predicted_value = input_market_value * (1 + ysp_score / 100)
            roi = predict_roi(input_market_value, predicted_value)
            st.metric("תחזית ROI עתידי", f"{roi}%")

        transfermarkt_link = generate_transfermarkt_link(row['Player'], row.get('Squad', ''))
        st.markdown(f"[🔗 מצא שחקן ב־Transfermarkt]({transfermarkt_link})")

        save_search(row['Player'], ysp_score)

        club_query = st.text_input("הקלד שם קבוצה (חלק מהשם):", key="club_input").strip().lower()
        matching_clubs = [c for c in clubs_df["Club"].unique() if match_text(club_query, c)]

        if club_query and matching_clubs:
            selected_club = st.selectbox("בחר קבוצה מתוך התוצאות:", matching_clubs)
            club_data = clubs_df[clubs_df["Club"] == selected_club]
            if not club_data.empty:
                club_row = club_data.iloc[0]
                fit_score = calculate_fit_score(player_row=row, club_row=club_row)
                st.metric("רמת התאמה חזויה לקבוצה", f"{fit_score}%")

        st.markdown("---")
        st.subheader("📊 10 המועדונים המתאימים ביותר לשחקן")
        scores = []
        for _, club_row in clubs_df.iterrows():
            score = calculate_fit_score(player_row=row, club_row=club_row)
            scores.append((club_row["Club"], score))
        top_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
        top_df = pd.DataFrame(top_scores, columns=["Club", "Fit Score"])

        st.bar_chart(top_df.set_index("Club"))
        csv = top_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 הורד את כל ההתאמות כ־CSV", data=csv, file_name=f"{row['Player']}_club_fits.csv", mime='text/csv')
    else:
        if player_query:
            st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

    st.caption("הנתונים מבוססים על ניתוח אלגוריתמי לצרכים חינוכיים ואנליטיים בלבד.")

mode = st.sidebar.radio("בחר מצב:", ("חיפוש שחקנים", "היסטוריית חיפושים"))
if mode == "חיפוש שחקנים":
    run_player_search()
elif mode == "היסטוריית חיפושים":
    show_search_history()
