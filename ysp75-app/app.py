import streamlit as st
import pandas as pd
import os

# שליפת קובץ נתונים
@st.cache_data
def load_data():
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ערכי ייחוס לעמדות
benchmarks = {
    "DF": {"Tkl": 50, "Int": 50, "Clr": 120, "Blocks": 30, "Min": 3000, "Gls": 3, "Ast": 2},
    "MF": {"Gls": 10, "Ast": 10, "Succ": 50, "KP": 50, "Min": 3000},
    "FW": {"Gls": 20, "Ast": 15, "Succ": 40, "KP": 40, "Min": 3000}
}

st.title("FstarVfootball – מדד סיכויי הצלחה לשחקנים צעירים (YSP-75)")

player_input = st.text_input("הכנס שם שחקן (פרטי או משפחה):").strip().lower()

if player_input:
    filtered_df = df[df["Player"].str.lower().str.contains(player_input)]

    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            name = row["Player"]
            league = row["Comp"]
            age = row["Age"]
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

            st.subheader(f"שחקן: {name}")
            st.write(f"ליגה: {league}")
            st.write(f"גיל: {age}")
            st.write(f"עמדה: {position}")
            st.write(f"דקות משחק: {minutes}")
            st.write(f"גולים: {goals}")
            st.write(f"בישולים: {assists}")
            st.write(f"דריבלים מוצלחים: {dribbles}")
            st.write(f"מסירות מפתח: {key_passes}")

            score = 0

            if "DF" in position:
                bm = benchmarks["DF"]
                score = (
                    (tackles / bm["Tkl"]) * 20 +
                    (interceptions / bm["Int"]) * 20 +
                    (clearances / bm["Clr"]) * 20 +
                    (blocks / bm["Blocks"]) * 10 +
                    (minutes / bm["Min"]) * 10 +
                    (goals / bm["Gls"]) * 10 +
                    (assists / bm["Ast"]) * 10
                )
            elif "MF" in position:
                bm = benchmarks["MF"]
                score = (
                    (goals / bm["Gls"]) * 20 +
                    (assists / bm["Ast"]) * 20 +
                    (dribbles / bm["Succ"]) * 20 +
                    (key_passes / bm["KP"]) * 20 +
                    (minutes / bm["Min"]) * 20
                )
            elif "FW" in position:
                bm = benchmarks["FW"]
                score = (
                    (goals / bm["Gls"]) * 30 +
                    (assists / bm["Ast"]) * 25 +
                    (dribbles / bm["Succ"]) * 15 +
                    (key_passes / bm["KP"]) * 15 +
                    (minutes / bm["Min"]) * 15
                )
            else:
                score = (goals * 3 + assists * 2 + minutes / 250)

            # התאמות גיל
            if age <= 20:
                score *= 1.1
            elif age <= 23:
                score *= 1.05

            # בונוס לליגות בכירות
            top_leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
            if any(lg in league for lg in top_leagues):
                score *= 1.2

            score = min(round(score, 2), 100)

            st.metric("מדד YSP-75", score)

            if age > 26 and score >= 85:
                st.success("טופ אירופי בהווה – שחקן מוכח ברמה גבוהה.")
            elif score >= 85:
                st.success("טופ אירופי – שחקן ברמת עילית, כדאי לעקוב ברצינות.")
            elif score >= 75:
                st.info("כישרון בקנה מידה עולמי – שווה מעקב.")
            elif score >= 65 or (goals >= 5 and assists >= 5):
                st.warning("פוטנציאל אירופי – דרושה יציבות נוספת.")
            else:
                st.write("דורש מעקב נוסף והבשלה.")

            st.write("---")
    else:
        st.error("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

st.caption("הנתונים נלקחו מ־Kaggle ומעובדים לצורכי הערכה חינוכית בלבד.")
