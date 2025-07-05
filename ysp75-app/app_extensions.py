import streamlit as st
import urllib.parse

def match_text(query, text):
    return query.lower() in str(text).lower()

def market_value_section(player_name: str) -> float | None:
    st.markdown("---")
    st.subheader("הזן שווי שוק ידני לשחקן (אפשרי)")

    manual_value = st.number_input(
        label=f"שווי שוק (באירו) לשחקן {player_name}",
        min_value=0.0,
        step=100000.0,
        format="%.2f",
        help="אם לא תזין ערך, השווי האוטומטי מהמאגר ישמש בחישוב.",
        key=f"manual_value_{player_name}"
    )
    if manual_value == 0.0:
        return None
    # המרה למיליוני אירו אם המשתמש הזין ערך כמו 90 (למשל)
    if manual_value >= 90 and manual_value < 1000:
        manual_value = manual_value * 1_000_000
    return manual_value

def generate_transfermarkt_search_url(player_name: str) -> str:
    query = f"site:transfermarkt.com {player_name}"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://duckduckgo.com/?q={encoded_query}"

def show_transfermarkt_link(player_name: str):
    url = generate_transfermarkt_search_url(player_name)
    link_html = f'''
    <div style="margin-top:10px; margin-bottom:5px;">
        <a href="{url}" target="_blank" style="font-weight:bold; font-size:18px; color:#1a73e8; text-decoration:none;">
            עמוד שחקן ב-Transfermarkt: {player_name}
        </a>
    </div>
    '''
    credit_html = '''
    <div style="font-size:10px; color:gray; font-style:italic;">
        חיפוש אוטומטי באמצעות מנוע DuckDuckGo
    </div>
    '''
    st.markdown(link_html, unsafe_allow_html=True)
    st.markdown(credit_html, unsafe_allow_html=True)

def calculate_ysp_score(row):
    # הקוד המלא לחישוב YSP-75 הגולמי כפי שהיה בקוד המקורי
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

def calculate_weighted_ysp_score(row, manual_market_value=None):
    # משקלל את מדד YSP עם שווי שוק (כמו שהוסבר)
    gross_score = calculate_ysp_score(row)
    market_value = row.get("MarketValue", 0)
    if manual_market_value is not None:
        market_value = manual_market_value
    # ניקח שווי שוק מרבי של 220 מיליון אירו (לשקלול)
    max_market_value = 220_000_000
    market_value_ratio = min(market_value / max_market_value, 1.0)

    # משקל גבוה יותר לביצועים הגולמיים (70%), ושווי שוק (30%)
    weighted_score = gross_score * 0.7 + (market_value_ratio * 100) * 0.3

    # אם הגולמי 100 והשווי מעל 90 מיליון => שומר על 100 (כפי שביקשת)
    if gross_score >= 100 and market_value >= 90_000_000:
        weighted_score = 100

    return round(min(weighted_score, 100), 2)

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
        # שווי שוק לא כולל בהתאמה לקבוצה
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

    return round(min(score, 100), 2)
