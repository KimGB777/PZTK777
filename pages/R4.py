#pages/R4.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json

def render():
    st.title("🔒 R4참고 (Google Sheet 편집)")
    # 비밀번호 인증
    correct_pw = os.environ.get("R4PW") or st.secrets.get("R4PW", "")
    if "r4_auth" not in st.session_state:
        st.session_state.r4_auth = False
    if not st.session_state.r4_auth:
        pw = st.text_input("비밀번호 입력", type="password")
        if st.button("접속") and pw == correct_pw:
            st.session_state.r4_auth = True
            st.experimental_rerun()
        st.stop()

    # 구글 시트 연결
    gcp_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON") or st.secrets["GCP_SERVICE_ACCOUNT_JSON"]
    service_account_info = json.loads(gcp_json)
    creds = Credentials.from_service_account_info(service_account_info)
    gc = gspread.authorize(creds)
    sheet_url = os.environ.get("GSHEETS_URL") or st.secrets["GSHEETS_URL"]
    sh = gc.open_by_url(sheet_url)
    worksheet = sh.worksheet("note")  # 시트명 맞게 수정

    # 데이터 표시
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    st.dataframe(df)

    # 행 추가 예시
    st.subheader("행 추가")
    col1 = st.text_input("새로운 컬럼1")
    col2 = st.text_input("새로운 컬럼2")
    if st.button("행 추가"):
        worksheet.append_row([col1, col2])
        st.success("추가 완료!")
        st.experimental_rerun()

    # 행 삭제 예시
    st.subheader("행 삭제")
    row_num = st.number_input("삭제할 행 번호(1부터)", min_value=1, max_value=len(df), value=1)
    if st.button("행 삭제"):
        worksheet.delete_rows(row_num)
        st.warning("삭제 완료!")
        st.experimental_rerun()
