import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    return pd.read_csv(path)

df = load_data()

st.title("FstarVfootball – מדד סיכויי הצלחה לשחקנים צעירים (YSP-75)")

# קלט שם
name_input = st.text_input("הכנס שם שחקן (פרטי או משפחה):").strip().lower()

if name_input:
    # חיפוש לפי התאמה חלקית לאותיות קטנות
    matches = df[df['name'].str.lower().str.contains(name_input)]

    if matches.empty:
        st.error("שחקן לא נמצא. נסה שם אחר.")
    elif len(matches) == 1:
        selected_row = matches.iloc[0]
    else:
        # מציג רשימה לבחירה לפי שם וגיל
        options = [f"{row['name']} (גיל: {row['age']})" for _, row in matches.iterrows()]
        choice = st.selectbox("בחר שחקן מתוך הרשימה:", options)

        selected_row = matches.iloc[options.index(choice)]

    # הצגת נתוני השחקן שנבחר
    st.subheader(f"שחקן: {selected_row['name']}")
    st.write(f"ליגה: {selected_row['league']}")
    st.write(f"גיל: {selected_row['age']}")
    st.write(f"דקות משחק: {selected_row['minutes']}")
    st.write(f"גולים: {selected_row['goals']}")
    st.write(f"בישולים: {selected_row['assists']}")

    dribbles = selected_row['dribbles_successful'] if 'dribbles_successful' in selected_row else 0
    key_passes = selected_row['key_passes'] if 'key_passes' in selected_row else 0

    st.write(f"דריבלים מוצלחים: {dribbles}")
    st.write(f"מסירות מפתח: {key_passes}")
    st.write("---")

    score = (
        selected_row['goals'] * 4 +
        selected_row['assists'] * 3 +
        dribbles * 1.5 +
        key_passes * 1.5 +
        selected_row['minutes'] / 300
    )

    if selected_row['age'] <= 20:
        score *= 1.1
    elif selected_row['age'] <= 23:
        score *= 1.05

    top_leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    if selected_row['league'] in top_leagues:
        score *= 1.2

    if selected_row['goals'] >= 5 and selected_row['assists'] >= 5 and score < 65:
        score = 65

    st.metric("מדד YSP-75", round(score, 2))

    if selected_row['age'] > 26 and score >= 85:
        st.success("שחקן מוכח ברמה אירופית גבוהה (טופ בהווה).")
    elif score >= 85:
        st.success("טופ אירופי – שחקן מוכח ברמת עילית.")
    elif score >= 75:
        st.info("כישרון בקנה מידה אירופאי – ביצועים מצוינים.")
    elif score >= 65:
        st.warning("ביצועים מעודדים – שווה מעקב.")
    else:
        st.write("דורש מעקב נוסף והבשלה.")

st.caption("הנתונים נלקחו מ־Kaggle ומעובדים לצורכי הערכה חינוכית בלבד.")
