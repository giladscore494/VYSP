import streamlit as st
import os
import pandas as pd
from search_history import save_search, show_search_history
import app_extensions  # נניח שכל הפונקציות המורחבות שלך ב-app_extensions.py

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

def run_player_search():
    st.title("FstarVfootball")

    df = load_data()
    clubs_df = load_club_data()

    player_query = st.text_input("הקלד שם שחקן (חלק מהשם):", key="player_input").strip()
    matching_players = df[df["Player"].apply(lambda name: match_text(player_query, name))]

    if player_query and not matching_players.empty:
        if len(matching_players) == 1:
            selected_player = matching_players["Player"].iloc[0]
        else:
            selected_player = st.selectbox("בחר שחקן מתוך תוצאות החיפוש:", matching_players["Player"].tolist())

        row = df[df["Player"] == selected_player].iloc[0]

        # 1. חישוב YSP-75 גולמי
        ysp_raw_score = app_extensions.calculate_ysp_score(row)
        st.metric("מדד YSP-75 (גולמי)", ysp_raw_score)

        # קישור לטרנספרמרקט (DuckDuckGo + Google fallback)
        tm_link = app_extensions.get_transfermarkt_link(selected_player)
        if tm_link:
            st.markdown(f"[קישור לטרנספרמרקט של {selected_player}]({tm_link})")
        else:
            st.info("לא נמצא קישור אוטומטי לטרנספרמרקט.")

        # 2. הזנת שווי שוק ידני (באירו, עם המרה למיליונים אם >=90)
        manual_market_value = app_extensions.market_value_section(selected_player)

        # 3. כפתור לאישור שווי שוק
        ysp_weighted_score = None
        if manual_market_value is not None:
            # המרה לאירו אם המשתמש הכניס רק מספר קטן מ-90, אחרת נניח שהוזן במיליונים
            if manual_market_value < 90:
                manual_market_value_eur = manual_market_value
            else:
                manual_market_value_eur = manual_market_value * 1_000_000

            if st.button("חשב מדד YSP-75 משוקלל עם שווי שוק"):
                ysp_weighted_score = app_extensions.calculate_ysp_score_with_market_value(row, manual_market_value_eur)
                st.metric("מדד YSP-75 (משוקלל)", ysp_weighted_score)

                # שמירת החיפוש עם המדד המשוקלל
                save_search(selected_player, ysp_weighted_score)

        # 4. רק אם חישוב משוקלל בוצע – הצגת אפשרות להזין שם קבוצה ולבדוק התאמה
        if ysp_weighted_score is not None:
            club_query = st.text_input("הקלד שם קבוצה (חלק מהשם):", key="club_input").strip().lower()
            matching_clubs = [c for c in clubs_df["Club"].unique() if match_text(club_query, c)]

            if club_query and matching_clubs:
                selected_club = st.selectbox("בחר קבוצה מתוך התוצאות:", matching_clubs)
                club_data = clubs_df[clubs_df["Club"] == selected_club]
                if not club_data.empty:
                    club_row = club_data.iloc[0]
                    # חישוב התאמה ללא שקלול שווי שוק
                    fit_score = app_extensions.calculate_fit_score(player_row=row, club_row=club_row, include_market_value=False)
                    st.metric("רמת התאמה חזויה לקבוצה", f"{fit_score}%")
                    if fit_score >= 85:
                        st.success("התאמה מצוינת – סביר שיצליח במערכת הזו.")
                    elif fit_score >= 70:
                        st.info("התאמה סבירה – עשוי להסתגל היטב.")
                    else:
                        st.warning("התאמה נמוכה – דרושה התאמה טקטית או סבלנות.")
            elif club_query:
                st.warning("לא נמצאו קבוצות תואמות.")
        else:
            st.info("הזן שווי שוק ואשר לחישוב מדד משוקלל ולהמשך התאמת קבוצות.")

        # הצגת פרטים בסיסיים על השחקן
        st.subheader(f"שחקן: {row['Player']}")
        st.write(f"ליגה: {row['Comp']} | גיל: {row['Age']} | עמדה: {row['Pos']}")
        st.write(f"דקות: {row['Min']} | גולים: {row['Gls']} | בישולים: {row['Ast']}")
        st.write(f"דריבלים מוצלחים: {row['Succ']} | מסירות מפתח: {row['KP']}")

    else:
        if player_query:
            st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

    st.caption("הנתונים מבוססים על ניתוח אלגוריתמי לצרכים חינוכיים ואנליטיים בלבד.")

mode = st.sidebar.radio("בחר מצב:", ("חיפוש שחקנים", "היסטוריית חיפושים"))

if mode == "חיפוש שחקנים":
    run_player_search()
elif mode == "היסטוריית חיפושים":
    show_search_history()
