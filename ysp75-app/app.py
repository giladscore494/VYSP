import streamlit as st
import pandas as pd

# טוען את הקובץ
@st.cache_data
def load_data():
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    return pd.read_csv(path)

df = load_data()

st.title("FstarVfootball – מדד סיכויי הצלחה לשחקנים צעירים (YSP-75)")

# קלט שם שחקן
player_name = st.text_input("הכנס שם שחקן:").strip().lower()

if player_name:
    # סינון לפי שם
    results = df[df['name'].str.lower().str.contains(player_name)]

    if not results.empty:
        for idx, row in results.iterrows():
            st.subheader(f"שחקן: {row['name']}")
            st.write(f"ליגה: {row['league']}")
            st.write(f"גיל: {row['age']}")
            st.write(f"דקות משחק: {row['minutes']}")
            st.write(f"גולים: {row['goals']}")
            st.write(f"בישולים: {row['assists']}")
            st.write(f"דריבלים מוצלחים: {row.get('dribbles_successful', 0)}")
            st.write(f"מסירות מפתח: {row.get('key_passes', 0)}")
            st.write("---")

            # חישוב מדד
            score = (
                row['goals'] * 4 +
                row['assists'] * 3 +
                row.get('dribbles_successful', 0) * 1.5 +
                row.get('key_passes', 0) * 1.5 +
                row['minutes'] / 300
            )

            # התאמת משקל לפי גיל
            if row['age'] <= 20:
                score *= 1.1
            elif row['age'] <= 23:
                score *= 1.05

            # בונוס לליגות הבכירות
            top_leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
            if row['league'] in top_leagues:
                score *= 1.2

            # הגבלת תקרה
            score = min(score, 100)

            st.metric("מדד YSP-75", round(score, 2))

            # תיאור מילולי עם הבחנה לגיל
            if row['age'] > 26:
                st.success("שחקן מוכח בטופ האירופי – כבר בשיאו.")
            else:
                if score >= 75:
                    st.success("טופ אירופי – שחקן ברמת עילית, כדאי לעקוב ברצינות.")
                elif score >= 65:
                    st.info("כישרון ברמה עולמית – שווה מעקב והתפתחות.")
                elif score >= 55:
                    st.warning("כישרון עם פוטנציאל – נדרש יציבות והתקדמות.")
                else:
                    st.write("שחקן שצריך עוד זמן ומעקב לפני מסקנות.")

    else:
        st.error("שחקן לא נמצא. נסה שם אחר.")

st.caption("הנתונים נלקחו מ־Kaggle ומעובדים לצורכי הערכה חינוכית בלבד.")
