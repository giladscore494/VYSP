import streamlit as st
import os
import pandas as pd
import datetime
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

def match_text(query, text):
    return query.lower() in str(text).lower()

def calculate_fit_score(player_row, club_row):
    score = 0
    weights = {
        "style": 0.20,
        "pressing": 0.15,
        "def_line": 0.10,
        "xg_match": 0.15,
        "pass_match": 0.10,
        "formation_role": 0.15,
        "age_dynamics": 0.05,
        "personal_style": 0.10
    }

    position = str(player_row["Pos"])
    minutes = player_row["Min"]
    goals = player_row["Gls"]
    assists = player_row["Ast"]
    dribbles = player_row["Succ"]
    key_passes = player_row["KP"]
    xg = player_row.get("xG", 0)
    xag = player_row.get("xAG", 0)
    age = player_row["Age"]

    formation = club_row["Common Formation"]
    style = club_row["Playing Style"]
    press = club_row["Pressing Style"]
    def_line = club_row["Defensive Line Depth"]
    pass_acc = club_row["Pass Accuracy (%)"]
    team_xg = club_row["Team xG per Match"]

    style_score = 50
    if "Attacking" in style and "FW" in position:
        style_score = 100
    elif "Balanced" in style and "MF" in position:
        style_score = 100
    elif "Low Block" in style and "DF" in position:
        style_score = 90
    score += style_score * weights["style"]

    press_score = 50
    if "High Press" in press and "FW" in position:
        press_score = 100
    elif "Mid Block" in press and "MF" in position:
        press_score = 80
    score += press_score * weights["pressing"]

    def_score = 50
    if "High" in def_line and "DF" in position:
        def_score = 100
    elif "Medium" in def_line and "MF" in position:
        def_score = 80
    score += def_score * weights["def_line"]

    xg_score = 50
    if team_xg >= 1.8 and "FW" in position and goals >= 5:
        xg_score = 100
    elif team_xg <= 1.2 and "DF" in position:
        xg_score = 100
    elif team_xg >= 1.4 and "MF" in position:
        xg_score = 80
    score += xg_score * weights["xg_match"]

    pass_score = 50
    try:
        player_pass_style = (key_passes + dribbles) / (minutes / 90 + 1e-6)
        if pass_acc >= 87 and player_pass_style >= 2.5:
            pass_score = 100
        elif pass_acc <= 82 and player_pass_style < 1.5:
            pass_score = 90
        elif pass_acc >= 85 and player_pass_style >= 1.5:
            pass_score = 80
    except:
        pass
    score += pass_score * weights["pass_match"]

    form_score = 50
    if "4-3-3" in formation and "FW" in position:
        form_score = 100
    elif "4-2-3-1" in formation and "MF" in position:
        form_score = 100
    elif "3-5-2" in formation and "DF" in position:
        form_score = 100
    score += form_score * weights["formation_role"]

    age_score = 50
    if age <= 20 and "Attacking" in style:
        age_score = 100
    elif age <= 23:
        age_score = 80
    score += age_score * weights["age_dynamics"]

    personal_score = 50
    personal_index = ((goals + assists) + dribbles * 0.5 + key_passes * 0.5 + xg * 2 + xag) / (minutes / 90 + 1e-6)
    if personal_index >= 3.5:
        personal_score = 100
    elif personal_index >= 2.0:
        personal_score = 80
    elif personal_index <= 1.0:
        personal_score = 60
    score += personal_score * weights["personal_style"]

    return round(min(score, 100), 2)

def calculate_ysp_score(row):
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
    age = row["Age"]
    league = row["Comp"]

    benchmarks = {
        "GK": {"Min": 3000, "Clr": 30, "Tkl": 10, "Blocks": 15},
        "DF": {"Tkl": 50, "Int": 50, "Clr": 120, "Blocks": 30, "Min": 3000, "Gls": 3, "Ast": 2},
        "MF": {"Gls": 10, "Ast": 10, "Succ": 50, "KP": 50, "Min": 3000},
        "FW": {"Gls": 20, "Ast": 15, "Succ": 40, "KP": 40, "Min": 3000}
    }

    league_weights = {
        "eng Premier League": 1.00,
        "es La Liga": 0.98,
        "de Bundesliga": 0.96,
        "it Serie A": 0.95,
        "fr Ligue 1": 0.93
    }

    ysp_score = 0
    if "GK" in position:
        bm = benchmarks["GK"]
        ysp_score = (
            (minutes / bm["Min"]) * 40 +
            (clearances / bm["Clr"]) * 20 +
            (tackles / bm["Tkl"]) * 20 +
            (blocks / bm["Blocks"]) * 20
        )
    elif "DF" in position:
        bm = benchmarks["DF"]
        ysp_score = (
            (tackles / bm["Tkl"]) * 18 +
            (interceptions / bm["Int"]) * 18 +
            (clearances / bm["Clr"]) * 18 +
            (blocks / bm["Blocks"]) * 10 +
            (minutes / bm["Min"]) * 10 +
            (goals / bm["Gls"]) * 13 +
            (assists / bm["Ast"]) * 13
        )
    elif "MF" in position:
        bm = benchmarks["MF"]
        ysp_score = (
            (goals / bm["Gls"]) * 20 +
            (assists / bm["Ast"]) * 20 +
            (dribbles / bm["Succ"]) * 20 +
            (key_passes / bm["KP"]) * 20 +
            (minutes / bm["Min"]) * 20
        )
    elif "FW" in position:
        bm = benchmarks["FW"]
        ysp_score = (
            (goals / bm["Gls"]) * 30 +
            (assists / bm["Ast"]) * 25 +
            (dribbles / bm["Succ"]) * 15 +
            (key_passes / bm["KP"]) * 15 +
            (minutes / bm["Min"]) * 15
        )
    else:
        ysp_score = (goals * 3 + assists * 2 + minutes / 250)

    if minutes > 0:
        contribution_per_90 = ((goals + assists + dribbles * 0.5 + key_passes * 0.5) / minutes) * 90
        if contribution_per_90 >= 1.2:
            ysp_score += 15
        elif contribution_per_90 >= 0.9:
            ysp_score += 10
        elif contribution_per_90 >= 0.6:
            ysp_score += 5

    if age <= 20:
        ysp_score *= 1.1
    elif age <= 23:
        ysp_score *= 1.05

    league_weight = league_weights.get(league.strip(), 0.9)
    ysp_score *= league_weight
    return min(round(ysp_score, 2), 100)

def run_player_search():
    st.title("FstarVfootball")

    df = load_data()
    clubs_df = load_club_data()

    player_query = st.text_input("הקלד שם שחקן (חלק מהשם):", key="player_input").strip().lower()
    matching_players = df[df["Player"].apply(lambda name: match_text(player_query, name))]

    if player_query and not matching_players.empty:
        if len(matching_players) == 1:
            selected_player = matching_players["Player"].iloc[0]
        else:
            selected_player = st.selectbox("בחר שחקן מתוך תוצאות החיפוש:", matching_players["Player"].tolist())

        row = df[df["Player"] == selected_player].iloc[0]

        ysp_score = calculate_ysp_score(row)
        st.metric("מדד YSP-75", ysp_score)

        # שמירת החיפוש עם הציון
        save_search(selected_player, ysp_score)

        st.subheader(f"שחקן: {row['Player']}")
        st.write(f"ליגה: {row['Comp']} | גיל: {row['Age']} | עמדה: {row['Pos']}")
        st.write(f"דקות: {row['Min']} | גולים: {row['Gls']} | בישולים: {row['Ast']}")
        st.write(f"דריבלים מוצלחים: {row['Succ']} | מסירות מפתח: {row['KP']}")

        club_query = st.text_input("הקלד שם קבוצה (חלק מהשם):", key="club_input").strip().lower()
        matching_clubs = [c for c in clubs_df["Club"].unique() if match_text(club_query, c)]

        if club_query and matching_clubs:
            selected_club = st.selectbox("בחר קבוצה מתוך התוצאות:", matching_clubs)
            club_data = clubs_df[clubs_df["Club"] == selected_club]
            if not club_data.empty:
                club_row = club_data.iloc[0]
                fit_score = calculate_fit_score(player_row=row, club_row=club_row)
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
        if player_query:
            st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

    st.caption("הנתונים מבוססים על ניתוח אלגוריתמי לצרכים חינוכיים ואנליטיים בלבד.")

def forecast_analysis():
    st.title("מערכת ניתוח תחזיות - FstarVfootball")

    DATA_DIR = "ysp75-app"
    DEFAULT_FORECAST_FILE = os.path.join(DATA_DIR, "forecast_data.csv")
    HISTORY_FILE = os.path.join(DATA_DIR, "forecast_history.csv")

    uploaded_file = st.file_uploader("העלה קובץ תחזיות CSV (או השתמש בקובץ שמור)", type="csv")

    if uploaded_file is not None:
        forecast_df = pd.read_csv(uploaded_file)

        forecast_df["Upload_Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if os.path.exists(HISTORY_FILE):
            history_df = pd.read_csv(HISTORY_FILE)
            history_df = pd.concat([history_df, forecast_df], ignore_index=True)
        else:
            history_df = forecast_df
        history_df.to_csv(HISTORY_FILE, index=False)
        st.success("הקובץ נשמר בהיסטוריה.")

    else:
        if os.path.exists(DEFAULT_FORECAST_FILE):
            forecast_df = pd.read_csv(DEFAULT_FORECAST_FILE)
            st.info(f"נטען קובץ תחזיות שמור: {DEFAULT_FORECAST_FILE}")
        else:
            st.warning("לא הועלה קובץ תחזיות וגם לא נמצא קובץ שמור.")
            return

    st.subheader("טבלת תחזיות ותוצאות אמת")
    st.dataframe(forecast_df)

    def calc_accuracy(pred_col, actual_col):
        df = forecast_df.dropna(subset=[pred_col, actual_col])
        if df.empty:
            return None
        correct = (df[pred_col] == df[actual_col]).sum()
        total = len(df)
        return correct / total * 100

    st.subheader("אחוזי דיוק")

    for col in ["Actual_Progress", "Actual_Transfer"]:
        acc = calc_accuracy(col, col)
        if acc is not None:
            st.metric(f"אחוז דיוק ב-{col}", f"{acc:.2f}%")
        else:
            st.write(f"אין נתונים ל-{col}")

    bins = [0, 60, 75, 85, 100]
    labels = ["נמוך", "בינוני", "גבוה", "גבוה מאוד"]

    forecast_df["YSP_Category"] = pd.cut(forecast_df["YSP_Score"], bins=bins, labels=labels, include_lowest=True)
    grouped = forecast_df.groupby("YSP_Category")[["Actual_Progress", "Actual_Transfer"]].mean() * 100

    st.subheader("דיוק ממוצע לפי קטגוריות YSP:")
    st.bar_chart(grouped)

    csv_data = forecast_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 הורד דו\"ח תחזיות כ־CSV", data=csv_data, file_name="forecast_report.csv", mime="text/csv")

    if st.checkbox("הצג היסטוריית תחזיות קודמות"):
        if os.path.exists(HISTORY_FILE):
            history_df = pd.read_csv(HISTORY_FILE)
            st.subheader("היסטוריית תחזיות")
            st.dataframe(history_df)
        else:
            st.info("אין היסטוריית תחזיות לשמירה עדיין.")

mode = st.sidebar.radio("בחר מצב:", ("חיפוש שחקנים", "ניתוח תחזיות", "היסטוריית חיפושים"))

if mode == "חיפוש שחקנים":
    run_player_search()
elif mode == "ניתוח תחזיות":
    forecast_analysis()
elif mode == "היסטוריית חיפושים":
    show_search_history()
