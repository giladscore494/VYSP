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

# ערכי בנצ'מרק וניקוד לכל מדד לפי עמדה
benchmarks = {
    "GK": {"Min": 3000, "Clr": 30, "Tkl": 10, "Blocks": 15, "Gls": 1, "Ast": 1, "Succ": 5, "KP": 2, "Int": 5},
    "DF": {"Tkl": 50, "Int": 50, "Clr": 120, "Blocks": 30, "Min": 3000, "Gls": 3, "Ast": 2, "Succ": 10, "KP": 5},
    "MF": {"Gls": 10, "Ast": 10, "Succ": 50, "KP": 50, "Min": 3000, "Tkl": 20, "Int": 20, "Clr": 10},
    "FW": {"Gls": 20, "Ast": 15, "Succ": 40, "KP": 40, "Min": 3000, "Tkl": 5, "Blocks": 5}
}

weights = {
    "GK": {"Min": 25, "Clr": 20, "Tkl": 15, "Blocks": 15, "Gls": 5, "Ast": 5, "Succ": 5, "KP": 5, "Int": 5},
    "DF": {"Tkl": 20, "Int": 15, "Clr": 15, "Blocks": 10, "Min": 10, "Gls": 10, "Ast": 10, "Succ": 5, "KP": 5},
    "MF": {"Gls": 15, "Ast": 15, "Succ": 15, "KP": 15, "Min": 15, "Tkl": 10, "Int": 10, "Clr": 5},
    "FW": {"Gls": 30, "Ast": 20, "Succ": 15, "KP": 10, "Min": 10, "Tkl": 5, "Blocks": 5}
}

# דירוג איכות ליגות (משפיע על משקל ציונים)
league_weights = {
    "eng Premier League": 1.00,
    "es La Liga": 0.98,
    "de Bundesliga": 0.96,
    "it Serie A": 0.95,
    "fr Ligue 1": 0.93
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

            # קביעת סוג עמדה
            role = "FW"  # ברירת מחדל
            for r in ["GK", "DF", "MF", "FW"]:
                if r in position:
                    role = r
                    break

            bm = benchmarks[role]
            w = weights[role]

            # חישוב מדד YSP
            score = 0
            score += (minutes / bm.get("Min", 1)) * w.get("Min", 0)
            score += (goals / bm.get("Gls", 1)) * w.get("Gls", 0)
            score += (assists / bm.get("Ast", 1)) * w.get("Ast", 0)
            score += (dribbles / bm.get("Succ", 1)) * w.get("Succ", 0)
            score += (key_passes / bm.get("KP", 1)) * w.get("KP", 0)
            score += (tackles / bm.get("Tkl", 1)) * w.get("Tkl", 0)
            score += (interceptions / bm.get("Int", 1)) * w.get("Int", 0)
            score += (clearances / bm.get("Clr", 1)) * w.get("Clr", 0)
            score += (blocks / bm.get("Blocks", 1)) * w.get("Blocks", 0)

            # התאמות גיל
            if age <= 20:
                score *= 1.1
            elif age <= 23:
                score *= 1.05

            # התאמה לפי איכות הליגה
            league_weight = league_weights.get(league.strip(), 0.9)
            score *= league_weight

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

