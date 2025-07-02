# pages/R4.py

import streamlit as st
import pandas as pd
import hashlib
import time
import logging
from streamlit_gsheets import GSheetsConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """SHA-256으로 해시 생성"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """입력 비밀번호와 해시 비교"""
    return hash_password(password) == hashed

@st.cache_resource
def get_gsheets_conn():
    """st.connection으로 GSheetsConnection 객체 반환"""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        logger.error(f"Google Sheets 연결 실패: {e}")
        st.error("Google Sheets 연결에 실패했습니다. 설정을 확인하세요.")
        return None

def check_session_timeout(minutes: int = 30) -> bool:
    """관리자 세션 타임아웃 검사"""
    if "r4_login_time" in st.session_state:
        if time.time() - st.session_state.r4_login_time > minutes * 60:
            st.session_state.r4_auth = False
            st.session_state.pop("r4_login_time", None)
            st.warning("세션이 만료되었습니다. 다시 로그인하세요.")
            return False
    return True

def render():
    """R4 관리 페이지 렌더링"""
    st.set_page_config(page_title="⚙️ R4 관리", layout="wide")
    st.title("⚙️ R4 관리 (Google Sheets 편집)")

    # 초기화
    if "r4_auth" not in st.session_state:
        st.session_state.r4_auth = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0

    # 인증된 경우 세션 타임아웃 확인
    if st.session_state.r4_auth and not check_session_timeout():
        return

    # 로그인 폼
    if not st.session_state.r4_auth:
        st.info("🔐 관리자 인증 필요")
        if st.session_state.login_attempts >= 5:
            st.error("⚠️ 로그인 시도 초과")
            if st.button("재시도"):
                st.session_state.login_attempts = 0
                st.rerun()
            return

        pwd = st.text_input("관리자 비밀번호", type="password", key="r4_pwd")
        if st.button("로그인"):
            stored_hash = st.secrets.get("R4PW_HASH", "")
            if stored_hash and verify_password(pwd, stored_hash):
                st.session_state.r4_auth = True
                st.session_state.r4_login_time = time.time()
                st.session_state.login_attempts = 0
                st.success("✅ 로그인 성공!")
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                st.error(f"❌ 잘못된 비밀번호 ({st.session_state.login_attempts}/5)")
        return

    # 인증 완료 UI
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success("🔓 관리자 인증됨")
    with col2:
        if st.button("로그아웃"):
            st.session_state.r4_auth = False
            st.session_state.pop("r4_login_time", None)
            st.rerun()

    # Google Sheets 연결
    conn = get_gsheets_conn()
    if conn is None:
        return

    # 워크시트 선택
    worksheet = st.selectbox(
        "편집할 워크시트 선택",
        options=["note", "daily", "weekly", "monthly"],
        index=0
    )

    # 시트 로드
    try:
        df = conn.read(worksheet=worksheet)
    except Exception as e:
        st.error(f"워크시트 로드 실패: {e}")
        logger.error(f"워크시트 '{worksheet}' 로드 오류: {e}")
        return

    st.subheader(f"📋 '{worksheet}' 편집")
    # 데이터프레임 편집 UI
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="gsheet_editor"
    )

    # 변경사항 저장
    if st.button("✅ 변경사항 저장"):
        try:
            conn.update(worksheet=worksheet, data=edited_df)
            st.success("변경사항이 Google Sheets에 저장되었습니다!")
        except Exception as e:
            st.error(f"저장 실패: {e}")
            logger.error(f"Google Sheets 업데이트 오류: {e}")
