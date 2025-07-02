import streamlit as st
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="daily")
# 데이터 업데이트
conn.update(worksheet="daily", data=df)