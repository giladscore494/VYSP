import streamlit as st
import pandas as pd
import os

DATA_DIR = "ysp75-app"
DEFAULT_FORECAST_FILE = os.path.join(DATA_DIR, "forecast_data.csv")

st.set_page_config(page_title="FstarVfootball - ניתוח תחזיות", layout="wide")

st.title("מערכת ניתוח תחזיות - FstarVfootball")

uploaded_file = st.file_uploader("העלה קובץ תחזיות CSV (או השתמש בקובץ שמור)", type="csv")

if uploaded_file is not None:
    forecast_df = pd.read_csv(uploaded_file)
else:
    if os.path.exists(DEFAULT_FORECAST_FILE):
        forecast_df = pd.read_csv(DEFAULT_FORECAST_FILE)
        st.info(f"נטען קובץ תחזיות שמור: {DEFAULT_FORECAST_FILE}")
    else:
        st.warning("לא הועלה קובץ תחזיות וגם לא נמצא קובץ שמור.")
        st.stop()

st.subheader("דוגמה למבנה הקובץ:")
st.markdown("""
| Player       | YSP_Score | Fit_Score | Prediction_Date | Actual_Progress | Actual_Transfer |
|--------------|-----------|-----------|-----------------|-----------------|-----------------|
| Lamine Yamal | 85        | 90        | 2025-06-01      | 1               | 1               |
| John Doe     | 72        | 60        | 2025-05-15      | 0               | 0               |
""")

st.subheader("טבלת תחזיות ותוצאות אמת")
st.dataframe(forecast_df)

# פונקציות חישוב דיוק
def calc_accuracy(pred_col, actual_col):
    df = forecast_df.dropna(subset=[pred_col, actual_col])
    if df.empty:
        return None
    correct = (df[pred_col] == df[actual_col]).sum()
    total = len(df)
    return correct / total * 100

st.subheader("אחוזי דיוק")

# מדדים לדוגמה (1/0)
for col in ["Actual_Progress", "Actual_Transfer"]:
    acc = calc_accuracy(col, col)  # בעצם משווים עמודה לעצמה - תוכל להחליף לוגיקה אחרת
    if acc is not None:
        st.metric(f"אחוז דיוק ב-{col}", f"{acc:.2f}%")
    else:
        st.write(f"אין נתונים ל-{col}")

st.subheader("ניתוח מתקדם")

# אפשר להוסיף ניתוח מתקדם - לדוגמה: דיוק לפי טווחי ציונים
bins = [0, 60, 75, 85, 100]
labels = ["נמוך", "בינוני", "גבוה", "גבוה מאוד"]

forecast_df["YSP_Category"] = pd.cut(forecast_df["YSP_Score"], bins=bins, labels=labels, include_lowest=True)

grouped = forecast_df.groupby("YSP_Category")[["Actual_Progress", "Actual_Transfer"]].mean() * 100
st.write("דיוק ממוצע לפי קטגוריות YSP:")
st.bar_chart(grouped)

# אפשרות הורדת דו"ח
csv_data = forecast_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 הורד דו\"ח תחזיות כ־CSV", data=csv_data, file_name="forecast_report.csv", mime="text/csv")
