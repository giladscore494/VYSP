import streamlit as st
import requests
from bs4 import BeautifulSoup

def market_value_section(player_name: str) -> float | None:
    st.markdown("---")
    st.subheader("הזן שווי שוק ידני לשחקן (באירו)")

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
    return manual_value

def calculate_ysp_score(row):
    # כאן קוד החישוב הגולמי הקיים (לא משנה)
    pass

def calculate_ysp_score_with_market_value(row, manual_market_value):
    # חישוב משולב של YSP עם שקלול שווי שוק
    # פשוט דוגמה, לשלב את החישוב שלך
    ysp_raw = calculate_ysp_score(row)
    # למשל, לשקלל עם שווי שוק ידני במינימום ומקסימום
    weighted_score = ysp_raw + min(manual_market_value / 1_000_000, 20)
    return min(weighted_score, 100)

def calculate_fit_score(player_row, club_row, include_market_value=True):
    # חישוב ההתאמה - ללא שקלול שווי שוק כש include_market_value=False
    # תעתיק את הפונקציה שהכנת קודם כאן, ותוסיף בדיקה ל-include_market_value
    pass

def get_transfermarkt_link(player_name: str) -> str | None:
    # חיפוש ב-DuckDuckGo עם fallback לגוגל, מחזיר קישור אמין לטרנספרמרקט
    query = f"site:transfermarkt.com {player_name}"
    url = search_duckduckgo(query)
    if not url:
        url = search_google(query)
    return url

def search_duckduckgo(query: str) -> str | None:
    try:
        resp = requests.get(f"https://lite.duckduckgo.com/50x.html?e=3&q={query}")
        soup = BeautifulSoup(resp.text, "html.parser")
        a_tag = soup.find("a", href=True)
        if a_tag and "transfermarkt.com" in a_tag["href"]:
            return a_tag["href"]
    except Exception:
        pass
    return None

def search_google(query: str) -> str | None:
    try:
        # להוסיף פה בקשת חיפוש לגוגל (כגון דרך API חינמי או פשוט לנתח את HTML)
        # לשם הפשטות נחזיר None
        return None
    except Exception:
        return None
