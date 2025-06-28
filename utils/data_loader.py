# utils/data_loader.py
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def load_event_data(path: str):
    xl = pd.ExcelFile(path)
    daily   = pd.read_excel(xl, sheet_name="daily",   parse_dates=["Date"])
    weekly  = pd.read_excel(xl, sheet_name="weekly")
    monthly = pd.read_excel(xl, sheet_name="monthly")
    note    = pd.read_excel(xl, sheet_name="note")
    return daily, weekly, monthly, note
