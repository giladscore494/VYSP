import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- פונקציית התאמה כללית לטקסט ---
def match_text(query, text):
    return query.lower() in str(text).lower()


# --- יצירת קישור ל־Transfermarkt ---
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


# --- הזנת שווי שוק ידני ---
def market_value_section(player_name: str) -> float | None:
    st.markdown("---")
    st.subheader("הזן שווי שוק ידני לשחקן (אירו במיליונים)")
    manual_value = st.number_input(
        label=f"שווי שוק (במיליוני אירו) לשחקן {player_name}",
        min_value=0.0,
        step=1.0,
        format="%.1f",
        key=f"manual_value_{player_name}"
    )
    return None if manual_value == 0.0 else manual_value


# --- חישוב מדד YSP ---
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


# --- טאאב לחיפוש מתקדם ---
def run_advanced_search_tab():
    st.title("🔎 חיפוש מתקדם לפי ביצועים")

    # טעינת קובץ נתונים
    path = os.path.join("ysp75-app", "players_simplified_2025.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    positions = sorted(df["Pos"].unique())
    pos_filter = st.selectbox("בחר עמדה לסינון:", positions)

    filtered_df = df[df["Pos"] == pos_filter]

    # סינון מתקדם לפי נתונים מתאימים לעמדה
    if "GK" in pos_filter:
        min_clr = st.slider("ניקויים (Clearances)", 0, 100, 10)
        filtered_df = filtered_df[filtered_df["Clr"] >= min_clr]
    elif "DF" in pos_filter:
        min_tkl = st.slider("תיקולים", 0, 100, 20)
        min_blocks = st.slider("חסימות", 0, 50, 5)
        filtered_df = filtered_df[(filtered_df["Tkl"] >= min_tkl) & (filtered_df["Blocks"] >= min_blocks)]
    elif "MF" in pos_filter or "FW" in pos_filter:
        min_kp = st.slider("מסירות מפתח", 0, 100, 10)
        min_dribbles = st.slider("דריבלים מוצלחים", 0, 100, 10)
        filtered_df = filtered_df[(filtered_df["KP"] >= min_kp) & (filtered_df["Succ"] >= min_dribbles)]

    # סינון נוסף לפי גיל ו־xG צפוי
    min_age = st.slider("גיל מינימלי", 15, 30, 17)
    max_age = st.slider("גיל מקסימלי", 18, 30, 24)
    min_xg = st.slider("xG צפוי", 0.0, 1.5, 0.3)
    filtered_df = filtered_df[
        (filtered_df["Age"] >= min_age) & 
        (filtered_df["Age"] <= max_age) &
        (filtered_df["xG"] >= min_xg)
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
        market_value = st.number_input(f"💶 הזן שווי שוק נוכחי ב-מיליון אירו עבור {row['Player']}", min_value=0.0, step=0.1, format="%.2f", key=f"mv_{row['Player']}")
        if market_value > 0:
            predicted = (ysp / 100) * 80 + 20
            roi_label = "פוטנציאל רווח משמעותי" if predicted > market_value else "פוטנציאל רווח מתון או חסר"
            st.write(f"💡 {roi_label} (YSP: {ysp}, שווי נוכחי: {market_value}M)")

        st.markdown("---")
