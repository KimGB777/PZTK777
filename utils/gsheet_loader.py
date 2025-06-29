#utils/gsheet_loader.py
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Worksheet name mapping
SHEETS = {
    "daily":   "일일데이터",
    "weekly":  "반복이벤트",
    "monthly": "4주반복",
    "note":    "메모"
}

@st.cache_data(ttl=300)
def load_gsheet_data() -> dict[str, pd.DataFrame]:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dfs = {}
    for key, ws in SHEETS.items():
        df = conn.read(worksheet=ws, usecols=lambda _: True)
        if key == "daily" and "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        dfs[key] = df
    return dfs

