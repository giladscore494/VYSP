import streamlit as st
import os
import pandas as pd
import datetime

DATA_DIR = "ysp75-app"
SEARCH_HISTORY_FILE = os.path.join(DATA_DIR, "search_history.csv")

def ensure_search_history_file():
    if not os.path.exists(SEARCH_HISTORY_FILE):
        df = pd.DataFrame(columns=["Player", "YSP_Score", "Timestamp"])
        df.to_csv(SEARCH_HISTORY_FILE, index=False)
    else:
        df = pd.read_csv(SEARCH_HISTORY_FILE)
        required_cols = {"Player", "YSP_Score", "Timestamp"}
        existing_cols = set(df.columns)
        missing = required_cols - existing_cols
        if missing:
            for col in missing:
                df[col] = ""
            df.to_csv(SEARCH_HISTORY_FILE, index=False)

def save_search(player_name, ysp_score):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([{
        "Player": player_name,
        "YSP_Score": ysp_score,
        "Timestamp": now
    }])

    ensure_search_history_file()

    history_df = pd.read_csv(SEARCH_HISTORY_FILE)
    history_df = pd.concat([history_df, new_entry], ignore_index=True)
    history_df.to_csv(SEARCH_HISTORY_FILE, index=False)

def show_search_history():
    st.title("היסטוריית חיפושי שחקנים")

    if os.path.exists(SEARCH_HISTORY_FILE):
        history_df = pd.read_csv(SEARCH_HISTORY_FILE)

        counts = history_df.groupby(["Player", "YSP_Score"]).size().reset_index(name="מספר חיפושים")
        counts = counts.sort_values(by="מספר חיפושים", ascending=False)

        st.subheader("מספר חיפושים לפי שחקן וציוני YSP")
        st.dataframe(counts)

        if st.checkbox("הצג טבלת היסטוריה מפורטת"):
            st.subheader("טבלת חיפושים מלאה")
            st.dataframe(history_df)
    else:
        st.info("טרם קיימת היסטוריית חיפושים לשמירה.")
