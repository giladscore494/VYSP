import streamlit as st
import requests
from urllib.parse import quote_plus

def market_value_section(player_name: str) -> float | None:
    st.markdown("---")
    st.subheader("הזן שווי שוק ידני לשחקן (בשקלים או במיליוני אירו)")

    manual_value = st.number_input(
        label=f"שווי שוק לשחקן {player_name} (אם 90 או יותר, נחשב במיליוני אירו)",
        min_value=0.0,
        step=100000.0,
        format="%.2f",
        help="הזן שווי שוק ידני או השאר 0 לשימוש בשווי מהמאגר.",
        key=f"manual_value_{player_name}"
    )
    if manual_value >= 90:  # המרה לאירו (מיליונים)
        manual_value = manual_value * 1_000_000 * 4  # נניח 1 אירו=4 ש"ח
    elif manual_value == 0.0:
        return None
    return manual_value

def search_transfermarkt(player_name: str) -> str | None:
    """חיפוש אוטומטי של קישור Transfermarkt לשחקן עם fallback ל-DuckDuckGo."""
    query = quote_plus(f"{player_name} site:transfermarkt.com")
    google_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(google_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            text = resp.text
            # חיפוש קישורי TM מהתוצאה
            import re
            links = re.findall(r'href="(https://www.transfermarkt.com/[^"]+)"', text)
            if links:
                return links[0]
    except Exception:
        pass

    # fallback ל-DuckDuckGo
    ddg_url = f"https://duckduckgo.com/html/?q={query}"
    try:
        resp = requests.get(ddg_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            text = resp.text
            import re
            links = re.findall(r'href="(https://www.transfermarkt.com/[^"]+)"', text)
            if links:
                return links[0]
    except Exception:
        pass

    return None

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
