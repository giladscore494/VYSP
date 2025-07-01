import streamlit as st
import os
import requests

st.set_page_config(page_title="Fetch Players from API-Football", layout="wide")

API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {"x-apisports-key": API_KEY}

def fetch_all_players(league_id=39, season=2023):
    url = "https://v3.football.api-sports.io/players"
    players = []
    page = 1
    while True:
        params = {"league": league_id, "season": season, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            st.error(f"Error fetching data: {response.status_code}")
            break
        data = response.json()
        if not data["response"]:
            break
        players.extend(data["response"])
        if page >= data["paging"]["total"]:
            break
        page += 1
    return players

st.title("שלב 2: שליפת שחקנים מה-API")

league_id = st.number_input("בחר קוד ליגה", min_value=1, max_value=9999, value=39)
season = st.number_input("בחר עונה", min_value=2010, max_value=2030, value=2023)

if st.button("משוך שחקנים מה-API"):
    with st.spinner("מושך שחקנים..."):
        players = fetch_all_players(league_id=league_id, season=season)
        st.success(f"נמשכו {len(players)} שחקנים מה-API.")
        if players:
            st.subheader("3 שחקנים לדוגמה:")
            for p in players[:3]:
                st.json(p)
