import streamlit as st
import os
import pandas as pd
import app_extensions
from search_history import save_search, show_search_history

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

def run_player_search():
    st.title("FstarVfootball")

    df = load_data()
    clubs_df = load_club_data()

    player_query = st.text_input("הקלד שם שחקן (חלק מהשם):", key="player_input").strip()
    matching_players = df[df["Player"].apply(lambda name: app_extensions.match_text(player_query, name))]

    if player_query and not matching_players.empty:
        if len(matching_players) == 1:
            selected_player = matching_players["Player"].iloc[0]
        else:
            selected_player = st.selectbox("בחר שחקן מתוך תוצאות החיפוש:", matching_players["Player"].tolist())

        row = df[df["Player"] == selected_player].iloc[0]

        # חישוב ראשוני: YSP גולמי (ללא שווי שוק)
        ysp_gross = app_extensions.calculate_ysp_score(row)
        st.metric("מדד YSP-75", ysp_gross)

        # הזנת שווי שוק ידני + קישור לעמוד ב-Transfermarkt
        manual_value = app_extensions.market_value_section(selected_player)
        search_link = app_extensions.generate_transfermarkt_search_link(selected_player)
        st.markdown(f"[קישור חיפוש לשווי שוק ב-Transfermarkt](<{search_link}>)")

        # רק אם הזינו שווי שוק ידני, מחשבים YSP משוקלל
        if manual_value is not None:
            ysp_weighted = app_extensions.calculate_fit_score(row, None, manual_market_value=manual_value)
            st.metric("מדד YSP-75 משוקלל עם שווי שוק ידני", ysp_weighted)

            # אפשרות להזין שם קבוצה ולחשב מדד התאמה לקבוצה
            club_query = st.text_input("הקלד שם קבוצה (חלק מהשם):", key="club_input").strip()
            matching_clubs = [c for c in clubs_df["Club"].unique() if app_extensions.match_text(club_query, c)]

            if club_query and matching_clubs:
                selected_club = st.selectbox("בחר קבוצה מתוך התוצאות:", matching_clubs)
                club_data = clubs_df[clubs_df["Club"] == selected_club]
                if not club_data.empty:
                    club_row = club_data.iloc[0]
                    fit_score = app_extensions.calculate_fit_score(row, club_row, manual_market_value=manual_value)
                    st.metric("רמת התאמה חזויה לקבוצה", f"{fit_score}%")
                    if fit_score >= 85:
                        st.success("התאמה מצוינת – סביר שיצליח במערכת הזו.")
                    elif fit_score >= 70:
                        st.info("התאמה סבירה – עשוי להסתגל היטב.")
                    else:
                        st.warning("התאמה נמוכה – דרושה התאמה טקטית או סבלנות.")
            elif club_query:
                st.warning("לא נמצאו קבוצות תואמות.")

            # הצגת 10 המועדונים המתאימים ביותר (עם fit score)
            st.markdown("---")
            st.subheader("📊 10 המועדונים המתאימים ביותר לשחקן")
            scores = []
            for i, club_row in clubs_df.iterrows():
                score = app_extensions.calculate_fit_score(row, club_row, manual_market_value=manual_value)
                scores.append((club_row["Club"], score))
            scores.sort(key=lambda x: x[1], reverse=True)
            top_scores = scores[:10]
            top_df = pd.DataFrame(top_scores, columns=["Club", "Fit Score"])

            st.bar_chart(top_df.set_index("Club"))
            csv = top_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 הורד את כל ההתאמות כ־CSV", data=csv, file_name=f"{selected_player}_club_fits.csv", mime='text/csv')

        else:
            st.info("הזן שווי שוק ידני כדי לראות מדד YSP-75 משוקלל והתאמה לקבוצה.")

        # שמירת החיפוש עם הציון הגולמי בלבד (שווי שוק לא נשמר)
        save_search(selected_player, ysp_gross)

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
