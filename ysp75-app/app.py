import streamlit as st
import pandas as pd
import os

# שליפת קובץ נתונים
@st.cache_data
def load_data():
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()  # הסרת רווחים מהשמות
    return df

df = load_data()

st.title("FstarVfootball – מדד סיכויי הצלחה לשחקנים צעירים (YSP-75)")

# קלט שם
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

            # חישוב מדד לפי עמדה
            score = 0
            if "GK" in position:
                score = (minutes / 90) + blocks * 2 + clearances + tackles
            elif "DF" in position:
                score = (
                    tackles * 1.5 + interceptions * 1.5 + clearances * 1.2 +
                    blocks * 1.2 + minutes / 300 + goals * 2 + assists * 1.5
                )
            elif "MF" in position:
                score = (
                    goals * 3 + assists * 3 + dribbles * 1.5 + key_passes * 1.5 +
                    minutes / 250
                )
            elif "FW" in position:
                score = (
                    goals * 4 + assists * 3 + dribbles * 1.2 + key_passes * 1.2 +
                    minutes / 200
                )
            else:
                score = (goals * 3 + assists * 2 + minutes / 250)

            # התאמות לגיל
            if age <= 20:
                score *= 1.1
            elif age <= 23:
                score *= 1.05

            # בונוס לליגות בכירות
            top_leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
            if any(league_name in league for league_name in top_leagues):
                score *= 1.2

            # הגבלת מדד ל-100
            score = min(round(score, 2), 100)

            st.metric("מדד YSP-75", score)

            # תיאור
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
