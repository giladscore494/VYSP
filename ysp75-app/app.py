import streamlit as st
import pandas as pd

# נתיב לקובץ הנתונים
DATA_PATH = "players_simplified_2025.csv"

# דירוג הליגות - ציון איכות לליגה (ככל שגבוה יותר, כך טוב יותר)
LEAGUE_SCORES = {
    'Premier League': 1.0,
    'La Liga': 0.95,
    'Serie A': 0.9,
    'Bundesliga': 0.9,
    'Ligue 1': 0.85
}

# טען את הנתונים עם בדיקת תקינות
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH)
        return df.dropna(subset=["Player", "Age", "Min", "Gls", "Ast"])
    except Exception as e:
        st.error(f"\u274c שגיאה בטעינת הקובץ: {e}")
        st.stop()

# פונקציית חישוב מדד YSP-75
def calculate_ysp(row):
    try:
        age = float(row["Age"])
        minutes = float(row["Min"])
        goals = float(row["Gls"])
        assists = float(row["Ast"])
        league = row["Comp"]

        league_score = LEAGUE_SCORES.get(league, 0.7)
        offensive_contrib = (goals * 0.6 + assists * 0.4)
        minutes_factor = min(minutes / 1000, 1.0)
        age_factor = max(0, 1 - (age - 18) / 10)

        score = 100 * offensive_contrib * minutes_factor * age_factor * league_score
        return round(score, 2)
    except:
        return 0

# כותרת האפליקציה
st.title("🎯 YSP-75 – מדד סיכויי הצלחה לשחקן צעיר")
st.markdown("""
מדד YSP-75 מעריך את הפוטנציאל של שחקנים צעירים על סמך:
**גיל, ליגה, דקות משחק, גולים ובישולים.**

- ציון מעל **75**: טופ אירופי.
- ציון **65-75**: כישרון עולמי.
- ציון **55-65**: כישרון שצריך שיפור.
""")

# טען את הנתונים
players_df = load_data()

# קלט שם שחקן
name = st.text_input("הזן שם שחקן (באנגלית):")

if name:
    filtered = players_df[players_df['Player'].str.lower().str.contains(name.lower())]
    if filtered.empty:
        st.warning("\u26a0\ufe0f שחקן לא נמצא בקובץ")
    else:
        for _, row in filtered.iterrows():
            score = calculate_ysp(row)
            st.subheader(row['Player'])
            st.write(f"**ליגה:** {row['Comp']}")
            st.write(f"**גיל:** {row['Age']} | **דקות:** {row['Min']:.0f}")
            st.write(f"**שערים:** {row['Gls']} | **בישולים:** {row['Ast']}")
            st.metric("YSP-75 Score", score)

# קרדיט מקור הנתונים
st.markdown("---")
st.markdown("נתוני שחקנים נלקחו מהטבלה שהוזנה על ידי המשתמש לצורכי הדגמה בלבד.")
