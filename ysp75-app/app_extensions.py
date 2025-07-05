import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

def match_text(query, text):
    return query.lower() in str(text).lower()

def generate_transfermarkt_link(player_name: str) -> str | None:
    query = f"site:transfermarkt.com {player_name}"
    ddg_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
    try:
        res = requests.get(ddg_url, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = soup.find_all("a", class_="result__a", href=True)
            for a in results:
                href = a['href']
                if "transfermarkt.com" in href:
                    if href.startswith("/l/?kh="):
                        parsed = urllib.parse.urlparse(href)
                        q = urllib.parse.parse_qs(parsed.query).get('uddg', [None])[0]
                        if q:
                            return q
                    else:
                        return href
    except Exception:
        pass
    google_search = f"https://www.google.com/search?q=site:transfermarkt.com+{urllib.parse.quote_plus(player_name)}"
    return google_search

def market_value_section(player_name: str) -> float | None:
    st.markdown("---")
    st.subheader("הזן שווי שוק ידני לשחקן (אירו במיליונים)")

    manual_value = st.number_input(
        label=f"שווי שוק (במיליוני אירו) לשחקן {player_name}",
        min_value=0.0,
        step=1.0,
        format="%.1f",
        help="אם לא תזין ערך, השווי האוטומטי מהמאגר ישמש בחישוב.",
        key=f"manual_value_{player_name}"
    )
    if manual_value == 0.0:
        return None
    return manual_value

def calculate_fit_score(player_row, club_row, manual_market_value=None):
    score = 0
    weights = {
        "style": 0.20,
        "pressing": 0.15,
        "def_line": 0.10,
        "xg_match": 0.15,
        "pass_match": 0.10,
        "formation_role": 0.15,
        "age_dynamics": 0.05,
        "personal_style": 0.05,
        "roi_factor": 0.05
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
    market_value = player_row.get("MarketValue", 0)
    future_value = player_row.get("FutureValue", 0)

    if club_row is not None:
        formation = club_row["Common Formation"]
        style = club_row["Playing Style"]
        press = club_row["Pressing Style"]
        def_line = club_row["Defensive Line Depth"]
        pass_acc = club_row["Pass Accuracy (%)"]
        team_xg = club_row["Team xG per Match"]
    else:
        formation = ""
        style = ""
        press = ""
        def_line = ""
        pass_acc = 0
        team_xg = 0

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

    roi_score = 50
    try:
        base_value = manual_market_value if manual_market_value is not None else market_value
        if base_value > 0 and future_value > 0:
            roi = (future_value - base_value) / base_value
            if roi >= 1.0:
                roi_score = 100
            elif roi >= 0.5:
                roi_score = 80
            elif roi >= 0.2:
                roi_score = 65
        score += roi_score * weights["roi_factor"]
    except:
        pass

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
def run_advanced_search_tab():
    import os
    import pandas as pd
    import streamlit as st

    st.title("🔎 חיפוש מתקדם לפי ביצועים")

    # טעינת קובץ נתונים
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    positions = sorted(df["Pos"].unique())
    pos_filter = st.selectbox("בחר עמדה לסינון:", positions)

    filtered_df = df[df["Pos"] == pos_filter]

    # סינון מתקדם לפי נתונים מתאימים לעמדה - תמיד טווח קבוע!
    if "GK" in pos_filter:
        clr_range = st.slider("ניקויים (Clearances)", 0, 100, (0, 100))
        filtered_df = filtered_df[
            (filtered_df["Clr"] >= clr_range[0]) & (filtered_df["Clr"] <= clr_range[1])
        ]
    elif "DF" in pos_filter:
        tkl_range = st.slider("תיקולים", 0, 100, (0, 100))
        blocks_range = st.slider("חסימות", 0, 50, (0, 50))
        filtered_df = filtered_df[
            (filtered_df["Tkl"] >= tkl_range[0]) & (filtered_df["Tkl"] <= tkl_range[1]) &
            (filtered_df["Blocks"] >= blocks_range[0]) & (filtered_df["Blocks"] <= blocks_range[1])
        ]
    elif "MF" in pos_filter or "FW" in pos_filter:
        kp_range = st.slider("מסירות מפתח", 0, 100, (0, 100))
        dribbles_range = st.slider("דריבלים מוצלחים", 0, 100, (0, 100))
        filtered_df = filtered_df[
            (filtered_df["KP"] >= kp_range[0]) & (filtered_df["KP"] <= kp_range[1]) &
            (filtered_df["Succ"] >= dribbles_range[0]) & (filtered_df["Succ"] <= dribbles_range[1])
        ]

    # סינון נוסף לפי גיל ו־xG צפוי עם טווחים קבועים מראש
    age_range = st.slider("טווח גילאים", 15, 30, (17, 24))
    xg_range = st.slider("xG צפוי", 0.0, 1.5, (0.0, 1.5), step=0.01)
    filtered_df = filtered_df[
        (filtered_df["Age"] >= age_range[0]) & 
        (filtered_df["Age"] <= age_range[1]) &
        (filtered_df["xG"] >= xg_range[0]) & (filtered_df["xG"] <= xg_range[1])
    ]

    st.subheader(f"נמצאו {len(filtered_df)} שחקנים מתאימים")
    for _, row in filtered_df.iterrows():
        st.markdown(f"### {row['Player']} ({row['Age']}), {row['Pos']} - {row['Comp']}")
        ysp = calculate_ysp_score(row)
        st.write(f"🔢 מדד YSP: {ysp}")

        # קישור ל־Transfermarkt
        link = generate_transfermarkt_link(row["Player"])
        st.markdown(f"[🔗 עמוד Transfermarkt]({link})")

        # שווי שוק ו־ROI
        market_value = st.number_input(
            f"💶 הזן שווי שוק נוכחי ב-מיליון אירו עבור {row['Player']}",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            key=f"mv_{row['Player']}"
        )
        if market_value > 0:
            predicted = (ysp / 100) * 80 + 20
            roi_label = "פוטנציאל רווח משמעותי" if predicted > market_value else "פוטנציאל רווח מתון או חסר"
            st.write(f"💡 {roi_label} (YSP: {ysp}, שווי נוכחי: {market_value}M)")

        st.markdown("---")
