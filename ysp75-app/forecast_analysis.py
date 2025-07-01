import datetime

def forecast_analysis():
    st.title("מערכת ניתוח תחזיות - FstarVfootball")

    DATA_DIR = "ysp75-app"
    DEFAULT_FORECAST_FILE = os.path.join(DATA_DIR, "forecast_data.csv")
    HISTORY_FILE = os.path.join(DATA_DIR, "forecast_history.csv")

    uploaded_file = st.file_uploader("העלה קובץ תחזיות CSV (או השתמש בקובץ שמור)", type="csv")

    if uploaded_file is not None:
        forecast_df = pd.read_csv(uploaded_file)

        # שמירת ההעלאה להיסטוריה עם Timestamp
        forecast_df["Upload_Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if os.path.exists(HISTORY_FILE):
            history_df = pd.read_csv(HISTORY_FILE)
            history_df = pd.concat([history_df, forecast_df], ignore_index=True)
        else:
            history_df = forecast_df
        history_df.to_csv(HISTORY_FILE, index=False)
        st.success("הקובץ נשמר בהיסטוריה.")

    else:
        if os.path.exists(DEFAULT_FORECAST_FILE):
            forecast_df = pd.read_csv(DEFAULT_FORECAST_FILE)
            st.info(f"נטען קובץ תחזיות שמור: {DEFAULT_FORECAST_FILE}")
        else:
            st.warning("לא הועלה קובץ תחזיות וגם לא נמצא קובץ שמור.")
            return

    st.subheader("טבלת תחזיות ותוצאות אמת")
    st.dataframe(forecast_df)

    def calc_accuracy(pred_col, actual_col):
        df = forecast_df.dropna(subset=[pred_col, actual_col])
        if df.empty:
            return None
        correct = (df[pred_col] == df[actual_col]).sum()
        total = len(df)
        return correct / total * 100

    st.subheader("אחוזי דיוק")

    for col in ["Actual_Progress", "Actual_Transfer"]:
        acc = calc_accuracy(col, col)
        if acc is not None:
            st.metric(f"אחוז דיוק ב-{col}", f"{acc:.2f}%")
        else:
            st.write(f"אין נתונים ל-{col}")

    bins = [0, 60, 75, 85, 100]
    labels = ["נמוך", "בינוני", "גבוה", "גבוה מאוד"]

    forecast_df["YSP_Category"] = pd.cut(forecast_df["YSP_Score"], bins=bins, labels=labels, include_lowest=True)
    grouped = forecast_df.groupby("YSP_Category")[["Actual_Progress", "Actual_Transfer"]].mean() * 100

    st.subheader("דיוק ממוצע לפי קטגוריות YSP:")
    st.bar_chart(grouped)

    csv_data = forecast_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 הורד דו\"ח תחזיות כ־CSV", data=csv_data, file_name="forecast_report.csv", mime="text/csv")

    # הצגת היסטוריה שמורה
    if st.checkbox("הצג היסטוריית תחזיות קודמות"):
        if os.path.exists(HISTORY_FILE):
            history_df = pd.read_csv(HISTORY_FILE)
            st.subheader("היסטוריית תחזיות")
            st.dataframe(history_df)
        else:
            st.info("אין היסטוריית תחזיות לשמירה עדיין.")
