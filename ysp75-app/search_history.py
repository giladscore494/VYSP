import streamlit as st
import os
import pandas as pd
import datetime

DATA_DIR = "ysp75-app"
HISTORY_FILE = os.path.join(DATA_DIR, "search_history.csv")

def save_search(player_name):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([{"Player": player_name, "Timestamp": now}])

    if os.path.exists(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)
        history_df = pd.concat([history_df, new_entry], ignore_index=True)
    else:
        history_df = new_entry

    history_df.to_csv(HISTORY_FILE, index=False)

def show_search_history():
    st.title("היסטוריית חיפושי שחקנים")

    if os.path.exists(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)

        counts = history_df.groupby("Player").size().reset_index(name="מספר חיפושים")
        counts = counts.sort_values(by="מספר חיפושים", ascending=False)

        st.subheader("מספר חיפושים לפי שחקן")
        st.dataframe(counts)

        if st.checkbox("הצג טבלת היסטוריה מפורטת"):
            st.subheader("טבלת חיפושים מלאה")
            st.dataframe(history_df)
    else:
        st.info("טרם קיימת היסטוריית חיפושים לשמירה.")
