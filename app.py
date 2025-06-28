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
s
# KST 시간대
KST = timezone(timedelta(hours=9))
def get_kst_now():
    return datetime.now(timezone.utc).astimezone(KST)
kst_now = get_kst_now()

# 사이드바: 메뉴 & 자동 새로고침
dashboard_page_name="🏠대시보드"
calculator_page_name="🖩계산기(뭐 넣을지 고민중)"
r4page_name="⚙️R4참고(언젠가 개발)"
with st.sidebar:
    page = st.radio("메뉴 선택", [dashboard_page_name, calculator_page_name, r4page_name])


# 헤더
st.title("⚔️ LAST WAR:SURVIVAL PZTK #777")
col1, col2 = st.columns(2)
with col1:
    st.info(f"🕐 한국: {kst_now:%Y-%m-%d %H:%M:%S}")
with col2:
    server_now = kst_now - timedelta(hours=11)
    st.info(f"🕐 서버: {server_now:%Y-%m-%d %H:%M:%S}")

# 페이지 라우팅
if page == dashboard_page_name:
    from pages.Dashboard import render as render_dashboard
    render_dashboard()
elif page == calculator_page_name:
    from pages.Calculator import render as render_calculator
    render_calculator()
elif page == r4page_name:
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
        🎮 LAST WAR:SURVIVAL PZTK #777 연맹 대시보드 v3.0<br>
        Madeby @고체RHCP | Powered by Streamlit<br>
        최종 업데이트: {kst_now.strftime('%Y-%m-%d %H:%M:%S KST')}
    </div>
    """, 
    unsafe_allow_html=True
)