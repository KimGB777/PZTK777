'''
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

'''

# pages/R4.py
import streamlit as st
import pandas as pd
import gspread
import json
import os
import hashlib
import time
from google.oauth2.service_account import Credentials
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """패스워드를 SHA-256으로 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """패스워드 검증"""
    return hash_password(password) == hashed

def get_google_sheets_connection():
    """Google Sheets 연결 설정"""
    try:
        # 환경변수 또는 시크릿에서 인증 정보 가져오기
        sa_json = None
        if "GCP_SERVICE_ACCOUNT_JSON" in os.environ:
            sa_json = os.environ["GCP_SERVICE_ACCOUNT_JSON"]
        elif hasattr(st, 'secrets') and "GCP_SERVICE_ACCOUNT_JSON" in st.secrets:
            sa_json = st.secrets["GCP_SERVICE_ACCOUNT_JSON"]
        
        if not sa_json:
            st.error("Google Sheets 인증 정보가 설정되지 않았습니다.")
            return None, None
        
        # 인증 및 클라이언트 생성
        creds = Credentials.from_service_account_info(json.loads(sa_json))
        gc = gspread.authorize(creds)
        
        # 스프레드시트 URL 가져오기
        sheet_url = None
        if "GSHEETS_URL" in os.environ:
            sheet_url = os.environ["GSHEETS_URL"]
        elif hasattr(st, 'secrets') and "GSHEETS_URL" in st.secrets:
            sheet_url = st.secrets["GSHEETS_URL"]
        
        if not sheet_url:
            st.error("Google Sheets URL이 설정되지 않았습니다.")
            return None, None
        
        return gc, sheet_url
        
    except Exception as e:
        logger.error(f"Google Sheets 연결 오류: {e}")
        st.error(f"Google Sheets 연결 중 오류가 발생했습니다: {str(e)}")
        return None, None

def check_session_timeout(timeout_minutes: int = 30):
    """세션 타임아웃 확인"""
    if "r4_login_time" in st.session_state:
        login_time = st.session_state.r4_login_time
        current_time = time.time()
        if current_time - login_time > timeout_minutes * 60:
            st.session_state.r4_auth = False
            st.session_state.pop("r4_login_time", None)
            st.warning("세션이 만료되었습니다. 다시 로그인해주세요.")
            return False
    return True

def render() -> None:
    """R4 관리 페이지 렌더링"""
    st.title("⚙️ R4 관리 (Google Sheets 편집)")
    
    # 세션 상태 초기화
    if "r4_auth" not in st.session_state:
        st.session_state.r4_auth = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    
    # 세션 타임아웃 확인
    if st.session_state.r4_auth and not check_session_timeout():
        st.session_state.r4_auth = False
    
    # 인증 확인
    if not st.session_state.r4_auth:
        st.info("🔐 관리자 인증이 필요합니다.")
        
        # 로그인 시도 제한
        if st.session_state.login_attempts >= 5:
            st.error("⚠️ 로그인 시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요.")
            if st.button("재시도"):
                st.session_state.login_attempts = 0
                st.rerun()  # FIXED: st.experimental_rerun() -> st.rerun()
            return
        
        # 패스워드 입력
        password_input = st.text_input("관리자 비밀번호", type="password", key="r4_password")
        
        if st.button("로그인"):
            try:
                # 환경변수에서 해시된 패스워드 가져오기
                correct_hash = None
                if "R4PW_HASH" in os.environ:
                    correct_hash = os.environ["R4PW_HASH"]
                elif hasattr(st, 'secrets') and "R4PW_HASH" in st.secrets:
                    correct_hash = st.secrets["R4PW_HASH"]
                
                # 임시로 평문 패스워드도 지원 (보안상 좋지 않음)
                if not correct_hash:
                    correct_plain = None
                    if "R4PW" in os.environ:
                        correct_plain = os.environ["R4PW"]
                    elif hasattr(st, 'secrets') and "R4PW" in st.secrets:
                        correct_plain = st.secrets["R4PW"]
                    
                    if correct_plain and password_input == correct_plain:
                        st.session_state.r4_auth = True
                        st.session_state.r4_login_time = time.time()
                        st.session_state.login_attempts = 0
                        st.success("✅ 로그인 성공!")
                        st.rerun()  # FIXED: st.experimental_rerun() -> st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"❌ 잘못된 비밀번호입니다. ({st.session_state.login_attempts}/5)")
                else:
                    # 해시된 패스워드 검증
                    if verify_password(password_input, correct_hash):
                        st.session_state.r4_auth = True
                        st.session_state.r4_login_time = time.time()
                        st.session_state.login_attempts = 0
                        st.success("✅ 로그인 성공!")
                        st.rerun()  # FIXED: st.experimental_rerun() -> st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"❌ 잘못된 비밀번호입니다. ({st.session_state.login_attempts}/5)")
                        
            except Exception as e:
                logger.error(f"로그인 처리 오류: {e}")
                st.error("로그인 처리 중 오류가 발생했습니다.")
        
        return
    
    # 인증된 사용자 영역
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success("🔓 관리자로 로그인됨")
    with col2:
        if st.button("로그아웃"):
            st.session_state.r4_auth = False
            st.session_state.pop("r4_login_time", None)
            st.rerun()  # FIXED: st.experimental_rerun() -> st.rerun()
    
    # Google Sheets 연결
    try:
        gc, sheet_url = get_google_sheets_connection()
        if not gc or not sheet_url:
            return
        
        # 워크시트 선택
        worksheet_name = st.selectbox(
            "워크시트 선택", 
            ["note", "일일데이터", "반복이벤트", "4주반복"],
            index=0
        )
        
        # 워크시트 가져오기
        try:
            ws = gc.open_by_url(sheet_url).worksheet(worksheet_name)
            st.success(f"✅ '{worksheet_name}' 워크시트에 연결됨")
        except Exception as e:
            st.error(f"워크시트 '{worksheet_name}' 연결 실패: {str(e)}")
            return
        
        # 데이터 표시
        try:
            data = ws.get_all_records()
            if data:
                df = pd.DataFrame(data)
                st.subheader(f"📋 {worksheet_name} 데이터")
                st.dataframe(df, use_container_width=True)
                
                # 데이터 요약
                st.info(f"총 {len(df)}개 행, {len(df.columns)}개 열")
            else:
                st.warning("⚠️ 데이터가 없습니다.")
                df = pd.DataFrame()
        except Exception as e:
            st.error(f"데이터 로드 실패: {str(e)}")
            return
        
        st.divider()
        
        # 데이터 편집 기능
        tab1, tab2, tab3 = st.tabs(["➕ 행 추가", "🗑️ 행 삭제", "📊 데이터 분석"])
        
        with tab1:
            st.subheader("➕ 새 행 추가")
            if not df.empty:
                # 기존 컬럼 기반으로 입력 폼 생성
                new_row = {}
                cols = st.columns(min(3, len(df.columns)))
                
                for i, col_name in enumerate(df.columns):
                    with cols[i % 3]:
                        new_row[col_name] = st.text_input(f"{col_name}", key=f"add_{col_name}")
                
                if st.button("✅ 행 추가", key="add_row"):
                    try:
                        # 모든 값이 입력되었는지 확인
                        if all(value.strip() for value in new_row.values()):
                            ws.append_row(list(new_row.values()))
                            st.success("✅ 새 행이 추가되었습니다!")
                            time.sleep(1)  # 잠시 대기
                            st.rerun()  # FIXED: st.experimental_rerun() -> st.rerun()
                        else:
                            st.warning("⚠️ 모든 필드를 입력해주세요.")
                    except Exception as e:
                        st.error(f"행 추가 실패: {str(e)}")
            else:
                # 새 워크시트인 경우
                st.info("빈 워크시트입니다. 첫 번째 행을 추가해주세요.")
                col1, col2 = st.columns(2)
                with col1:
                    key = st.text_input("Key", key="new_key")
                with col2:
                    value = st.text_input("Value", key="new_value")
                
                if st.button("✅ 첫 행 추가"):
                    try:
                        ws.append_row([key, value])
                        st.success("✅ 첫 번째 행이 추가되었습니다!")
                        time.sleep(1)
                        st.rerun()  # FIXED: st.experimental_rerun() -> st.rerun()
                    except Exception as e:
                        st.error(f"행 추가 실패: {str(e)}")
        
        with tab2:
            st.subheader("🗑️ 행 삭제")
            if not df.empty:
                st.warning("⚠️ 삭제된 데이터는 복구할 수 없습니다!")
                
                # 삭제할 행 선택
                row_to_delete = st.selectbox(
                    "삭제할 행 선택 (첫 번째 열 기준)",
                    options=range(len(df)),
                    format_func=lambda x: f"행 {x+1}: {df.iloc[x, 0] if len(df.columns) > 0 else '빈 행'}"
                )
                
                if st.button("🗑️ 선택한 행 삭제", key="delete_row"):
                    try:
                        # Google Sheets는 1-based index + 헤더 행 고려
                        ws.delete_rows(row_to_delete + 2)  # +2 for header and 1-based index
                        st.success("✅ 행이 삭제되었습니다!")
                        time.sleep(1)
                        st.rerun()  # FIXED: st.experimental_rerun() -> st.rerun()
                    except Exception as e:
                        st.error(f"행 삭제 실패: {str(e)}")
            else:
                st.info("삭제할 데이터가 없습니다.")
        
        with tab3:
            st.subheader("📊 데이터 분석")
            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("전체 행 수", len(df))
                with col2:
                    st.metric("전체 열 수", len(df.columns))
                
                # 컬럼별 데이터 타입 분석
                st.subheader("컬럼 정보")
                for col in df.columns:
                    non_empty_count = df[col].notna().sum()
                    st.text(f"• {col}: {non_empty_count}/{len(df)} 개 데이터")
            else:
                st.info("분석할 데이터가 없습니다.")
        
    except Exception as e:
        logger.error(f"R4 페이지 오류: {e}")
        st.error("페이지 로드 중 오류가 발생했습니다.")
        st.info("문제가 지속되면 관리자에게 문의해주세요.")
    
    # 도움말
    with st.expander("📖 사용법"):
        st.markdown("""
        ### 🔧 R4 관리 기능
        
        **워크시트 선택**: 편집할 Google Sheets의 워크시트를 선택합니다.
        
        **행 추가**: 새로운 데이터 행을 추가할 수 있습니다.
        
        **행 삭제**: 기존 데이터 행을 삭제할 수 있습니다.
        
        **데이터 분석**: 현재 데이터의 기본 통계를 확인할 수 있습니다.
        
        ### ⚠️ 주의사항
        - 삭제된 데이터는 복구할 수 없습니다.
        - 세션은 30분 후 자동으로 만료됩니다.
        - 모든 변경사항은 즉시 Google Sheets에 반영됩니다.
        """)
