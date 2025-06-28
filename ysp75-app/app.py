import streamlit as st
import pandas as pd
import os

# טוען את הקובץ לפי נתיב מדויק
@st.cache_data
def load_data():
    path = os.path.join("ysp75-app", "players_data-2024_2025.csv")
    return pd.read_csv(path)

df = load_data()

st.title("FstarVfootball – מדד סיכויי הצלחה לשחקנים צעירים (YSP-75)")

# קלט חיפוש
player_input = st.text_input("הכנס שם שחקן (פרטי או משפחה):").strip().lower()

if player_input:
    filtered_df = df[df["Player"].str.lower().str.contains(player_input)]

    if filtered_df.empty:
        st.error("שחקן לא נמצא.")
    else:
        options = filtered_df["Player"].unique()
        selected_name = st.selectbox("בחר שחקן מהרשימה:", options)

        player_row = filtered_df[filtered_df["Player"] == selected_name].iloc[0]

        # הצגת נתונים
        st.subheader(f"שחקן: {player_row['Player']}")
        st.write(f"ליגה: {player_row['Comp']}")
        st.write(f"גיל: {player_row['Age']}")
        st.write(f"עמדה: {player_row['Pos']}")
        st.write(f"דקות משחק: {player_row['Min']}")
        st.write(f"גולים: {player_row['Gls']}")
        st.write(f"בישולים: {player_row['Ast']}")
        st.write(f"דריבלים מוצלחים: {player_row['Succ']}")
        st.write(f"מסירות מפתח: {player_row['KP']}")

        # חישוב מדד לפי עמדה
        position = player_row['Pos']
        score = 0

        if "GK" in position:
            score = (
                player_row['Min'] / 90 +
                player_row.get('Save%', 0) * 1.2 +
                player_row.get('CS', 0) * 5
            )
        elif "DF" in position:
            score = (
                player_row['Clr'] * 1.5 +
                player_row['Tkl'] * 1.2 +
                player_row['Int'] * 1.2 +
                player_row['Min'] / 300
            )
        elif "MF" in position:
            score = (
                player_row['Gls'] * 3 +
                player_row['Ast'] * 3 +
                player_row['Succ'] * 1.5 +
                player_row['KP'] * 1.5 +
                player_row['Min'] / 300
            )
        elif "FW" in position:
            score = (
                player_row['Gls'] * 4 +
                player_row['Ast'] * 3 +
                player_row['Succ'] * 1.5 +
                player_row['KP'] * 1.5 +
                player_row['Min'] / 300
            )
        else:
            score = (player_row['Gls'] + player_row['Ast']) * 2 + player_row['Min'] / 300

        # התאמות לפי גיל וליגה
        if player_row['Age'] <= 20:
            score *= 1.1
        elif player_row['Age'] <= 23:
            score *= 1.05

        if player_row['Comp'] in ["eng Premier League", "es La Liga", "it Serie A", "de Bundesliga", "fr Ligue 1"]:
            score *= 1.2

        score = round(score, 2)
        st.metric("מדד YSP-75", score)

        # תיאור מילולי
        if player_row["Age"] > 26 and score >= 85:
            st.success("שחקן טופ אירופי בהווה – ברמת עילית.")
        elif score >= 85:
            st.success("טופ אירופי – שחקן ברמת עילית, כדאי לעקוב ברצינות.")
        elif score >= 75:
            st.info("כישרון ברמה אירופית – שווה מעקב והתפתחות.")
        elif score >= 65:
            st.warning("כישרון עם פוטנציאל – דרוש פיתוח ויציבות.")
        else:
            st.write("דורש מעקב נוסף והבשלה.")

st.caption("הנתונים נלקחו מ־Kaggle ומעובדים לצורכי הערכה חינוכית בלבד.")
