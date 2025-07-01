import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="FstarVfootball – מדד YSP-75", layout="wide")

# CSS חיצוני
with open("style.css") as f:
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
