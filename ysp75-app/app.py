import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    return pd.read_csv(path)

df = load_data()

st.title("FstarVfootball – מדד סיכויי הצלחה לשחקנים צעירים (YSP-75)")

player_name = st.text_input("הכנס שם שחקן:").strip().lower()

if player_name:
    results = df[df['name'].str.lower().str.contains(player_name)]

    if not results.empty:
        for idx, row in results.iterrows():
            st.subheader(f"שחקן: {row['name']}")
            st.write(f"ליגה: {row['league']}")
            st.write(f"גיל: {row['age']}")
            st.write(f"דקות משחק: {row['minutes']}")
            st.write(f"גולים: {row['goals']}")
            st.write(f"בישולים: {row['assists']}")
            
            dribbles = row['dribbles_successful'] if 'dribbles_successful' in row else 0
            key_passes = row['key_passes'] if 'key_passes' in row else 0

            st.write(f"דריבלים מוצלחים: {dribbles}")
            st.write(f"מסירות מפתח: {key_passes}")
            st.write("---")

            score = (
                row['goals'] * 4 +
                row['assists'] * 3 +
                dribbles * 1.5 +
                key_passes * 1.5 +
                row['minutes'] / 300
            )

            if row['age'] <= 20:
                score *= 1.1
            elif row['age'] <= 23:
                score *= 1.05

            top_leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
            if row['league'] in top_leagues:
                score *= 1.2

            if row['goals'] >= 5 and row['assists'] >= 5 and score < 65:
                score = 65

            st.metric("מדד YSP-75", round(score, 2))

            if score >= 85:
                st.success("טופ אירופי – שחקן מוכח ברמת עילית.")
            elif score >= 75:
                st.info("כישרון בקנה מידה אירופאי – ביצועים מצוינים.")
            elif score >= 65:
                st.warning("ביצועים מעודדים – שווה מעקב.")
            else:
                st.write("דורש מעקב נוסף והבשלה.")
    else:
        st.error("שחקן לא נמצא. נסה שם אחר.")

st.caption("הנתונים נלקחו מ־Kaggle ומעובדים לצורכי הערכה חינוכית בלבד.")
