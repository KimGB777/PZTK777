# app.py
import streamlit as st
from datetime import datetime, timedelta, timezone
import logging
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="⚔️ PZTK 777",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚔️"
)

# 한국 시간대
KST = timezone(timedelta(hours=9))
def get_kst_now():
    return datetime.now(timezone.utc).astimezone(KST)

# Google Sheets 연결 객체 (캐시됨)
@st.cache_resource
def get_gsheets_conn():
    """Google Sheets 연결 객체 반환 (싱글톤)"""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        logger.error(f"Google Sheets 연결 실패: {e}")
        st.error("Google Sheets 연결에 실패했습니다. 설정을 확인해주세요.")
        return None

# 워크시트 로드 (15분 캐시)
@st.cache_data(ttl=900, max_entries=10, show_spinner=False)
def load_sheet(worksheet: str) -> pd.DataFrame:
    """워크시트 데이터 로드 (캐시됨)"""
    try:
        conn = get_gsheets_conn()
        if conn is None:
            return pd.DataFrame()
        return conn.read(worksheet=worksheet)
    except Exception as e:
        logger.error(f"워크시트 '{worksheet}' 로드 실패: {e}")
        return pd.DataFrame()

# 헤더
kst_now = get_kst_now()
st.title("⚔️ LAST WAR:SURVIVAL PZTK #777")
st.markdown("**라스트워:서바이벌 PZTK #777 연맹 홈페이지** | @고체RHCP")

col1, col2 = st.columns(2)
with col1:
    st.info(f"🕐 한국시간: {kst_now:%Y-%m-%d %H:%M:%S}")
with col2:
    server_now = kst_now - timedelta(hours=11)
    st.info(f"🕐 서버시간: {server_now:%Y-%m-%d %H:%M:%S}")

st.divider()

# 사이드바 메뉴
selection = st.sidebar.radio("메뉴 선택", ["대시보드", "참고자료/계산기", "일정관리(R4)"])

# 페이지 렌더링
try:
    if selection == "대시보드":
        import pages.Dashboard as dash
        dash.render(load_sheet)
    elif selection == "참고자료/계산기":
        import pages.Calculator as calc
        calc.render(load_sheet)
    elif selection == "일정관리(R4)":
        import pages.R4 as admin
        admin.render()
except Exception as e:
    logger.error(f"페이지 렌더링 오류: {e}")
    st.error("페이지를 불러오는 중 오류가 발생했습니다.")
    st.info("관리자에게 문의해주세요.")

# 푸터
st.divider()
st.markdown(
    f"""
    <div style='text-align: center; color: #666;'>
    🎮 LAST WAR:SURVIVAL PZTK #777 연맹 대시보드 🎮 
    ⚙️ Made by PZTK #777 고체RHCP ⚙️
    </div>
    """,
    unsafe_allow_html=True
)