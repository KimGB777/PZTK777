#utils/gsheet_loader.py
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit as st

# 시트 이름 ↔ DataFrame 매핑
SHEETS = {
    "daily"  : "일일데이터",      # 탭(Worksheet) 이름
    "weekly" : "반복이벤트",
    "monthly": "4주반복",
    "note"   : "메모"
}

@st.cache_data(ttl=300)
def load_gsheet_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    dfs = {}
    for key, wks_name in SHEETS.items():
        dfs[key] = conn.read(worksheet=wks_name, usecols=lambda x: True)
        # 날짜형 변환
        if key == "daily" and "Date" in dfs[key].columns:
            dfs[key]["Date"] = pd.to_datetime(dfs[key]["Date"])
    return dfs  # dict 반환
