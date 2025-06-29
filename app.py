# app.py
import streamlit as st
from datetime import datetime, timedelta, timezone
import os

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
    return datetime.now(timezone.utc).astimezone(KST)
kst_now = get_kst_now()

# 사이드바: 메뉴 & 자동 새로고침
page_name_0="🏠대시보드"
page_name_1="🖩계산기(뭐 넣을지 고민중)"
page_name_2="⚙️R4참고(언젠가 개발)"
with st.sidebar:
    page = st.radio("메뉴 선택", [page_name_0, page_name_1, page_name_2])


# 헤더
st.title("⚔️ LAST WAR:SURVIVAL PZTK #777")
col1, col2 = st.columns(2)
with col1:
    st.info(f"🕐 한국: {kst_now:%Y-%m-%d %H:%M:%S}")
with col2:
    server_now = kst_now - timedelta(hours=11)
    st.info(f"🕐 서버: {server_now:%Y-%m-%d %H:%M:%S}")
st.divider()

# 페이지 라우팅
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
    
    
# 푸터
st.divider()
st.markdown(
    f"""
    <div style='text-align: center; color: #666; font-size: 12px; margin: 20px 0;'>
        🎮 LAST WAR:SURVIVAL PZTK #777 연맹 대시보드 version x.x<br>
        Made by PZTK #777 고체RHCP | Powered by Streamlit<br>
    </div>
    """, 
    unsafe_allow_html=True
)