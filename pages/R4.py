#pages/R4.py
import streamlit as st
import pandas as pd
import gspread, json, os
from google.oauth2.service_account import Credentials

def render() -> None:
    st.title("⚙️ R4 참고 (Spreadsheet 편집)")

    # Password check
    if "r4_auth" not in st.session_state:
        st.session_state.r4_auth = False
    correct = os.environ.get("R4PW") or st.secrets.get("R4PW", "")
    if not st.session_state.r4_auth:
        if st.text_input("비밀번호", type="password") == correct:
            st.session_state.r4_auth = True
            st.experimental_rerun()
        st.stop()

    # Google Sheets connection via service account JSON
    sa_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON") or st.secrets["GCP_SERVICE_ACCOUNT_JSON"]
    creds = Credentials.from_service_account_info(json.loads(sa_json))
    gc = gspread.authorize(creds)

    sheet_url = os.environ.get("GSHEETS_URL") or st.secrets["GSHEETS_URL"]
    ws = gc.open_by_url(sheet_url).worksheet("note")

    df = pd.DataFrame(ws.get_all_records())
    st.dataframe(df, use_container_width=True)

    # Add row
    st.markdown("---")
    st.subheader("행 추가")
    k_col, v_col = st.columns(2)
    with k_col: k = st.text_input("Key")
    with v_col: v = st.text_input("Value")
    if st.button("추가") and k:
        ws.append_row([k, v])
        st.success("추가 완료")
        st.experimental_rerun()

    # Delete row
    st.markdown("---")
    st.subheader("행 삭제")
    idx = st.number_input("행 번호 (1부터)", min_value=1, max_value=len(df), value=1)
    if st.button("삭제"):
        ws.delete_rows(int(idx))
        st.warning("삭제 완료")
        st.experimental_rerun()
