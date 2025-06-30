# app.py
import streamlit as st
from datetime import datetime, timedelta, timezone
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="⚔️ LAST WAR:SURVIVAL PZTK #777",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚔️"
)

st.markdown("**라스트워:서바이벌 PZTK #777 연맹 홈페이지** | @고체RHCP")

# KST 시간대
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """현재 KST 시간을 반환합니다."""
    return datetime.now(timezone.utc).astimezone(KST)

try:
    kst_now = get_kst_now()
    
    # 사이드바: 메뉴 & 자동 새로고침
    page_name_0 = "🏠대시보드"
    page_name_1 = "🖩계산기"
    page_name_2 = "⚙️R4관리"
    
    with st.sidebar:
        page = st.radio("메뉴 선택", [page_name_0, page_name_1, page_name_2])
        
        # 자동 새로고침 설정
        auto_refresh = st.checkbox("자동 새로고침 (30초)", value=False)
        if auto_refresh:
            st.rerun()
    
    # 헤더
    st.title("⚔️ LAST WAR:SURVIVAL PZTK #777")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🕐 한국시간: {kst_now:%Y-%m-%d %H:%M:%S}")
    with col2:
        server_now = kst_now - timedelta(hours=11)
        st.info(f"🕐 서버시간: {server_now:%Y-%m-%d %H:%M:%S}")
    
    st.divider()
    
    # 페이지 라우팅 with error handling
    try:
        if page == page_name_0:
            from pages.Dashboard import render as render_dashboard
            render_dashboard()
        elif page == page_name_1:
            from pages.Calculator import render as render_calculator
            render_calculator()
        elif page == page_name_2:
            from pages.R4 import render as render_r4
            render_r4()
        else:
            from pages.Dashboard import render as render_dashboard
            render_dashboard()
    except Exception as e:
        logger.error(f"페이지 렌더링 오류: {e}")
        st.error("페이지를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
        st.info("문제가 지속되면 관리자에게 문의해주세요.")
    
    # 푸터
    st.divider()
    st.markdown(
        f"""
        <div style='text-align: center; color: #666;'>
        🎮 LAST WAR:SURVIVAL PZTK #777 연맹 대시보드 v2.0<br>
        Made by PZTK #777 고체RHCP | Powered by Streamlit<br>
        Last Updated: {kst_now:%Y-%m-%d %H:%M:%S} KST
        </div>
        """, 
        unsafe_allow_html=True
    )
    
except Exception as e:
    logger.error(f"앱 초기화 오류: {e}")
    st.error("애플리케이션을 초기화하는 중 오류가 발생했습니다.")
    st.info("브라우저를 새로고침하거나 관리자에게 문의해주세요.")
