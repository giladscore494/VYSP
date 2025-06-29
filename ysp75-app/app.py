import streamlit as st
import pandas as pd
import os

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
    parts = str(text).lower().split()
    return any(query in part for part in parts)

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

# ------------------- אפליקציה -------------------

df = load_data()
clubs_df = load_club_data()

st.title("FstarVfootball – מדד YSP-75 + מדד התאמה לקבוצה")

player_query = st.text_input("הקלד שם שחקן (חלק מהשם):").strip().lower()
matching_players = df[df["Player"].apply(lambda name: match_text(player_query, name))]

if player_query and not matching_players.empty:
    selected_player = st.selectbox("בחר שחקן מתוך תוצאות החיפוש:", matching_players["Player"].tolist())
    row = df[df["Player"] == selected_player].iloc[0]

    st.subheader(f"שחקן: {row['Player']}")
    st.write(f"ליגה: {row['Comp']}")
    st.write(f"גיל: {row['Age']}")
    st.write(f"עמדה: {row['Pos']}")
    st.write(f"דקות: {row['Min']} | גולים: {row['Gls']} | בישולים: {row['Ast']}")
    st.write(f"דריבלים מוצלחים: {row['Succ']} | מסירות מפתח: {row['KP']}")

    club_query = st.text_input("הקלד שם קבוצה (חלק מהשם):").strip().lower()
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
elif player_query:
    st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

# ⬇️ בודק התאמה מול כל הקבוצות
if player_query and not matching_players.empty:
    with st.expander("🔍 בדוק התאמה של השחקן מול כל הקבוצות במערכת"):
        if st.button("חשב התאמה לכל הקבוצות"):
            scores = []
            for i, club_row in clubs_df.iterrows():
                score = calculate_fit_score(player_row=row, club_row=club_row)
                scores.append((club_row["Club"], score))
            
            top_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
            top_df = pd.DataFrame(top_scores, columns=["Club", "Fit Score"])

            st.subheader("📊 10 הקבוצות המתאימות ביותר לשחקן")
            st.bar_chart(top_df.set_index("Club"))

            # כפתור הורדת CSV
            csv = pd.DataFrame(scores, columns=["Club", "Fit Score"]).to_csv(index=False).encode('utf-8')
            st.download_button("📥 הורד את כל ההתאמות כ־CSV", data=csv, file_name=f"{row['Player']}_club_fits.csv", mime='text/csv')

st.caption("הנתונים מבוססים על ניתוח אלגוריתמי לצרכים חינוכיים ואנליטיים בלבד.")
