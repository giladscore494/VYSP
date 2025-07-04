import streamlit as st
import urllib.parse

def manual_market_value_input(player_name: str):
    st.subheader("הזן שווי שוק ידני (אם יש):")
    default_value = ""
    input_value = st.text_input(
        f"שווי שוק ידני לשחקן {player_name} (מיליוני יורו):",
        value=default_value,
        help="הזן שווי שוק עכשווי במיליוני אירו, לדוגמה: 5.5"
    )
    try:
        val = float(input_value) if input_value.strip() != "" else None
    except ValueError:
        st.error("אנא הזן מספר חוקי לשווי השוק.")
        val = None
    return val

def generate_transfermarkt_url(player_name: str):
    base_url = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query="
    query = urllib.parse.quote(player_name)
    full_url = base_url + query
    return full_url

def display_market_value_and_link(player_name: str, manual_value):
    st.markdown(f"[לחץ כאן לחיפוש {player_name} ב-Transfermarkt]({generate_transfermarkt_url(player_name)})")
    if manual_value is not None:
        st.write(f"שווי שוק ידני שהוזן: **{manual_value} מיליון יורו**")
    else:
        st.info("לא הוזן שווי שוק ידני.")

def market_value_section(player_name: str):
    manual_value = manual_market_value_input(player_name)
    display_market_value_and_link(player_name, manual_value)
    return manual_value
