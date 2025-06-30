#pages/R4.py
import streamlit as st
import pandas as pd
import gspread, json, os
from google.oauth2.service_account import Credentials
import streamlit as st
import hashlib
import secrets
from functools import wraps

def hash_password(password: str, salt: str) -> str:
    """패스워드 해싱"""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """패스워드 검증"""
    return hash_password(password, salt) == hashed

def require_auth(func):
    """인증 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.error("🔒 관리자 권한이 필요합니다.")
            
            password = st.text_input("관리자 비밀번호", type="password", key="auth_password")
            if st.button("로그인"):
                # 실제 환경에서는 해시된 패스워드와 비교
                stored_hash = st.secrets.get("R4_PASSWORD_HASH", "")
                salt = st.secrets.get("R4_SALT", "")
                
                if stored_hash and verify_password(password, stored_hash, salt):
                    st.session_state.authenticated = True
                    st.session_state.auth_timestamp = time.time()
                    st.rerun()
                else:
                    st.error("❌ 잘못된 비밀번호입니다.")
            return
        
        # 세션 타임아웃 검사 (30분)
        if time.time() - st.session_state.get('auth_timestamp', 0) > 1800:
            st.session_state.authenticated = False
            st.error("🕐 세션이 만료되었습니다. 다시 로그인해주세요.")
            st.rerun()
            return
            
        return func(*args, **kwargs)
    return wrapper

@require_auth
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
