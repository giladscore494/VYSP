import streamlit as st
import pandas as pd

def run_app(df, clubs_df, calculate_fit_score, match_text):
    st.title("FstarVfootball – מדד YSP-75 + מדד התאמה לקבוצה")

    player_query = st.text_input("הקלד שם שחקן (חלק מהשם):").strip().lower()
    matching_players = df[df["Player"].apply(lambda name: match_text(player_query, name))]

    if player_query and not matching_players.empty:
        selected_player = st.selectbox("בחר שחקן מתוך תוצאות החיפוש:", matching_players["Player"].tolist())
        row = df[df["Player"] == selected_player].iloc[0]

        st.subheader(f"שחקן: {row['Player']}")
        st.write(f"ליגה: {row['Comp']} | גיל: {row['Age']} | עמדה: {row['Pos']}")
        st.write(f"דקות: {row['Min']} | גולים: {row['Gls']} | בישולים: {row['Ast']}")
        st.write(f"דריבלים מוצלחים: {row['Succ']} | מסירות מפתח: {row['KP']}")

        # חישוב מדד YSP-75
        ysp_score = calculate_ysp_score(row)
        st.metric("מדד YSP-75", ysp_score)

        # התאמה לקבוצה
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

                csv = pd.DataFrame(scores, columns=["Club", "Fit Score"]).to_csv(index=False).encode('utf-8')
                st.download_button("📥 הורד את כל ההתאמות כ־CSV", data=csv, file_name=f"{row['Player']}_club_fits.csv", mime='text/csv')
    else:
        if player_query:
            st.warning("שחקן לא נמצא. נסה שם מדויק או חלק ממנו.")

    st.caption("הנתונים מבוססים על ניתוח אלגוריתמי לצרכים חינוכיים ואנליטיים בלבד.")

def calculate_ysp_score(row):
    ysp_score = 0
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
