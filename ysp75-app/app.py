import streamlit as st
from players_data import fetch_players_from_api
import pandas as pd

# הגדרת עמוד
st.set_page_config(page_title="FstarVfootball - API Data", layout="wide")

@st.cache_data(show_spinner=False)
def load_data(league_id=39, season=2023):
    # מושך נתונים חיים מה-API
    try:
        df = fetch_players_from_api(league_id=league_id, season=season)
        return df
    except Exception as e:
        st.error(f"שגיאה בשליפת נתונים מה-API: {e}")
        return pd.DataFrame()  # מחזיר DataFrame ריק במקרה של שגיאה

@st.cache_data
def load_club_data():
    path = "ysp75-app/Updated_Club_Tactical_Dataset.csv"
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

def match_text(query, text):
    return query.lower() in str(text).lower()

def run_player_search():
    st.title("FstarVfootball")

    # בחר ליגה ועונה
    league_options = {
        "Premier League (eng)": 39,
        "La Liga (es)": 140,
        "Bundesliga (de)": 78,
        "Serie A (it)": 135,
        "Ligue 1 (fr)": 61
    }
    league_name = st.selectbox("בחר ליגה", options=list(league_options.keys()))
    league_id = league_options[league_name]

    season = st.number_input("בחר עונה", min_value=2019, max_value=2025, value=2023)

    with st.spinner("טוען נתונים מה-API..."):
        df = load_data(league_id=league_id, season=season)

    if df.empty:
        st.warning("לא נמצאו נתונים לשחקנים. נסה לבחור ליגה או עונה אחרת.")
        return

    clubs_df = load_club_data()

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

        # כאן תוכל להוסיף חישובים של מדד YSP או התאמה לפי הצורך

    else:
        if player_query:
            st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

    st.caption("הנתונים מבוססים על API-Football ועל מאגר טקטי מקומי.")

# תפריט בחירת מצב (ניתן להרחיב)
mode = st.sidebar.radio("בחר מצב:", ("חיפוש שחקנים",))

if mode == "חיפוש שחקנים":
    run_player_search()
