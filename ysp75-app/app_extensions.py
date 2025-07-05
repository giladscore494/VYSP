import streamlit as st
import requests
from bs4 import BeautifulSoup

def market_value_section(player_name: str) -> float | None:
    st.markdown("---")
    st.subheader("הזן שווי שוק ידני לשחקן (באירו)")

    manual_value_raw = st.number_input(
        label=f"שווי שוק (באירו) לשחקן {player_name} (לדוגמה, 90 עבור 90 מיליון)",
        min_value=0.0,
        step=1.0,
        format="%.2f",
        help="אם לא תזין ערך, השווי האוטומטי מהמאגר ישמש בחישוב.",
        key=f"manual_value_{player_name}"
    )

    submit = st.button("אשר שווי שוק")

    if submit:
        if manual_value_raw is None or manual_value_raw == 0:
            return None
        # המרה חכמה: אם הערך קטן מ-1000, נחשב כמיליוני יורו
        if manual_value_raw < 1000:
            manual_value = manual_value_raw * 1_000_000
        else:
            manual_value = manual_value_raw
        return manual_value
    else:
        return None

def find_transfermarkt_url(player_name):
    query = f"{player_name} site:transfermarkt.com"
    url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.find_all("a", class_="result__a", href=True)
        for a in results:
            href = a['href']
            if "transfermarkt.com" in href:
                return href
    except Exception:
        return None
    return None

def display_transfermarkt_link(player_name, existing_url=None):
    st.markdown("### קישור ל-Transfermarkt (לבדיקה והזנת שווי שוק)")
    url = existing_url or find_transfermarkt_url(player_name)
    if url:
        st.markdown(f"[לחץ כאן לעמוד ה-Transfermarkt של {player_name}]({url})")
    else:
        st.info("לא נמצא קישור אוטומטי ל-Transfermarkt עבור שחקן זה.")

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
