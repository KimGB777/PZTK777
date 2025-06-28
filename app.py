import streamlit as st
import pandas as pd
import datetime
import os
from datetime import timedelta, timezone

# ─────────────────────────────────────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚔️ LAST WAR:SURVIVAL PZTK #777",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚔️"
)

# ─────────────────────────────────────────────────────────────────────────────
# KST(UTC+9) 시간대 정의 및 유틸리티 함수
# ─────────────────────────────────────────────────────────────────────────────
KST = timezone(timedelta(hours=9))

def get_kst_now():
    #현재 KST 시간 반환
    utc_now = datetime.datetime.now(timezone.utc)
    return utc_now.astimezone(KST)

def get_secret(secret_name, default_value=""):
    #GitHub Secrets 또는 로컬 secrets.toml에서 값 가져오기
    # 1. 환경변수에서 먼저 확인 (GitHub Actions에서 설정됨)
    env_value = os.environ.get(secret_name)
    if env_value:
        return env_value
    
    # 2. 로컬 개발시 st.secrets에서 확인
    try:
        return st.secrets[secret_name]
    except (KeyError, FileNotFoundError):
        return default_value

# ─────────────────────────────────────────────────────────────────────────────
# 데이터 로드 함수
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = "./data/data_250628_1800.xlsx" # <<<<<<<<<<<<<<<<<   여기서 데이터 수정
@st.cache_data(ttl=300)  # 5분마다 데이터 갱신
def load_event_data(path: str):
    #이벤트 데이터를 로드하는 함수
    try:
        xl = pd.ExcelFile(path)
        daily_df = pd.read_excel(xl, sheet_name="daily", parse_dates=["Date"])
        weekly_df = pd.read_excel(xl, sheet_name="weekly")
        monthly_df = pd.read_excel(xl, sheet_name="monthly")
        note_df = pd.read_excel(xl, sheet_name="note")
        return daily_df, weekly_df, monthly_df, note_df
    except Exception as e:
        st.error(f"❌ 데이터 로드 실패: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Google Sheets 연동
@st.cache_data(ttl=300)
def load_data_from_gsheet():
    #Google Sheets에서 데이터 로드 (선택적 기능)
    try:
        # Google Sheets 연동 코드는 향후 확장 시 활용
        google_sheet_url = get_secret("GOOGLE_SHEET_URL", "")
        if google_sheet_url:
            # Google Sheets 연동 로직 구현 예정
            pass
        return None
    except Exception as e:
        st.sidebar.warning(f"Google Sheets 연동 실패: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# 메인 데이터 로드
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = "./data/data_250626_1500.xlsx"
daily_df, weekly_df, monthly_df, note_df = load_event_data(DATA_FILE)

# ─────────────────────────────────────────────────────────────────────────────
# 현재 KST 기준 시간 및 게임 일자 계산
# ─────────────────────────────────────────────────────────────────────────────
kst_now = get_kst_now()

# 게임 일자 계산 (KST 11:00~익일 11:00)
if kst_now.hour < 11:
    game_day = (kst_now - timedelta(days=1)).date()
else:
    game_day = kst_now.date()

# ─────────────────────────────────────────────────────────────────────────────
# 사이드바 설정
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📅 날짜 설정")
    selected_date = st.date_input("게임 일자 선택 (KST 11:00~익일 11:00)", value=game_day)
    
    # 자동 새로고침 옵션
    auto_refresh = st.checkbox("자동 새로고침 (5분)", value=False)
    if auto_refresh:
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────────────────────────────────────────
st.title("⚔️ LAST WAR:SURVIVAL PZTK #777")
st.markdown("**라스트워:서바이벌 PZTK #777 연맹 홈페이지** | @고체RHCP")

# 현재 시간과 게임 일자 표시
col_time1, col_time2 = st.columns(2)
with col_time1:
    st.info(f"🕐 현재시간: {kst_now:%Y년 %m월 %d일} {['월','화','수','목','금','토','일'][kst_now.weekday()]}요일 {kst_now:%H:%M:%S} KST")
with col_time2:
    if selected_date != game_day:
        st.warning(f"📅 선택된 게임 일자: {selected_date:%Y년 %m월 %d일} {['월','화','수','목','금','토','일'][selected_date.weekday()]}요일")

# 게임 일자 기간 표시
game_day_start = datetime.datetime.combine(selected_date, datetime.time(11, 0), tzinfo=KST)
game_day_end = game_day_start + timedelta(days=1)
st.caption(f"**게임 일자:** {selected_date:%Y-%m-%d} (KST 11:00 ~ {game_day_end:%m-%d %H:%M})")

# ─────────────────────────────────────────────────────────────────────────────
# 데이터 추출 및 정렬 함수
# ─────────────────────────────────────────────────────────────────────────────
def sort_content(content_list):
    """내용을 오름차순으로 정렬하는 함수"""
    if not content_list:
        return []
    
    all_lines = []
    for content in content_list:
        if pd.notna(content) and isinstance(content, str):
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            all_lines.extend(lines)
    
    return sorted(set(all_lines))  # 중복 제거 및 정렬

def format_content_display(content_lines, icon="•"):
    """콘텐츠를 표시용으로 포맷팅"""
    if not content_lines:
        return []
    
    formatted_lines = []
    for line in content_lines:
        if line.strip():
            formatted_lines.append(f"{icon} {line.strip()}")
    
    return formatted_lines

# ─────────────────────────────────────────────────────────────────────────────
# 데이터 추출
# ─────────────────────────────────────────────────────────────────────────────
weekday = selected_date.isoweekday()  # 1=월요일…7=일요일
week_index = (selected_date.isocalendar().week - 1) % 4

# 오늘 데이터 추출
today_weekly = weekly_df.loc[weekly_df["weekday"] == weekday]
today_daily = daily_df.loc[daily_df["Date"] == pd.Timestamp(selected_date)]
today_monthly = monthly_df.loc[monthly_df["mod(weeknum,4)"] == week_index]

# 1) 공지사항: announcement_weekely, announcement_daily, announcement_contd
notice_contents = []
if not today_daily.empty and "announcement_daily" in today_daily.columns:
    val = today_daily.iloc[0]["announcement_daily"]
    if pd.notna(val): notice_contents.append(val)
if not today_weekly.empty and "announcement_weekely" in today_weekly.columns:
    val = today_weekly.iloc[0]["announcement_weekely"]
    if pd.notna(val): notice_contents.append(val)
if not today_daily.empty and "announcement_montly" in today_daily.columns:
    val = today_daily.iloc[0]["announcement_monthly"]
    if pd.notna(val): notice_contents.append(val)
if not note_df.empty and "announcement_contd" in note_df.columns:
    val = note_df.iloc[0]["announcement_contd"]
    if pd.notna(val): notice_contents.append(val)
notice_sorted = sort_content(notice_contents)
notice = '\n'.join(notice_sorted) if notice_sorted else ""

# 2) 오늘의 일정: timetable_weekely, timetable_daily, timetable_contd, train_daily
schedule_contents = []
if not today_daily.empty and "timetable_daily" in today_daily.columns:
    val = today_daily.iloc[0]["timetable_daily"]
    if pd.notna(val): schedule_contents.append(val)
if not today_weekly.empty and "timetable_weekely" in today_weekly.columns:
    val = today_weekly.iloc[0]["timetable_weekely"]
    if pd.notna(val): schedule_contents.append(val)
if not note_df.empty and "timetable_contd" in note_df.columns:
    val = note_df.iloc[0]["timetable_contd"]
    if pd.notna(val): schedule_contents.append(val)
if not today_monthly.empty and "timetable_monthly" in today_monthly.columns:
    val = today_momthly.iloc[0]["timetable_monthly"]
    if pd.notna(val): schedule_contents.append(val)
    # 열차
if not today_daily.empty and "train_daily" in today_daily.columns:
    val = today_daily.iloc[0]["train_daily"]
    if pd.notna(val): schedule_contents.append(val)
    # 좀공
if not today_daily.empty and "zombie_daily" in today_daily.columns:
    val = today_daily.iloc[0]["zombie_daily"]
    if pd.notna(val): schedule_contents.append(val)
    # 군사훈련
if not today_daily.empty and "excercise_daily" in today_daily.columns:
    val = today_daily.iloc[0]["excercise_daily"]
    if pd.notna(val): schedule_contents.append(val)
schedule_sorted = sort_content(schedule_contents)
schedule = '\n'.join(schedule_sorted) if schedule_sorted else ""

# 3) 연맹대결: duel_weekely, duel_daily, duel_contd
duel_contents = []
if not today_daily.empty and "duel_daily" in today_daily.columns:
    val = today_daily.iloc[0]["duel_daily"]
    if pd.notna(val): duel_contents.append(val)
if not today_weekly.empty and "duel_weekely" in today_weekly.columns:
    val = today_weekly.iloc[0]["duel_weekely"]
    if pd.notna(val): duel_contents.append(val)
if not today_monthly.empty and "duel_monthly" in today_monthly.columns:
    val = today_monthly.iloc[0]["duel_monthly"]
    if pd.notna(val): duel_contents.append(val)
if not note_df.empty and "duel_contd" in note_df.columns:
    val = note_df.iloc[0]["duel_contd"]
    if pd.notna(val): duel_contents.append(val)
duel_sorted = sort_content(duel_contents)
duel_contd = '\n'.join(duel_sorted) if duel_sorted else ""

# 4) 이벤트: event_weekely, event_daily, package_weekly, event_monthly, package_monthly
# 4-1) 일반 이벤트 event_weekely, event_daily, 
event_contents = []
if not today_daily.empty and "event_daily" in today_daily.columns:
    val = today_daily.iloc[0]["event_daily"]
    if pd.notna(val): event_contents.append(val)    
if not today_weekly.empty and "event_weekely" in today_weekly.columns:
    val = today_weekly.iloc[0]["event_weekely"]
    if pd.notna(val): event_contents.append(val)
if not today_monthly.empty and "event_monthly" in today_monthly.columns:
    val = today_monthly.iloc[0]["event_monthly"]
    if pd.notna(val): event_contents.append(val)
if not note_df.empty and "event_contd" in note_df.columns:
    val = note_df.iloc[0]["event_contd"]
    if pd.notna(val): event_contents.append(val)
event_sorted = sort_content(event_contents)
event = '\n'.join(event_sorted) if event_sorted else ""

# 4-2) 과금 이벤트
package_contents = []
if not today_daily.empty and "package_daily" in today_daily.columns:
    val = today_daily.iloc[0]["package_daily"]
    if pd.notna(val): package_contents.append(val)    
if not today_weekly.empty and "package_weekely" in today_weekly.columns:
    val = today_weekly.iloc[0]["package_weekely"]
    if pd.notna(val): package_contents.append(val)
if not today_monthly.empty and "package_monthly" in today_monthly.columns:
    val = today_monthly.iloc[0]["package_monthly"]
    if pd.notna(val): package_contents.append(val)
if not note_df.empty and "package_contd" in note_df.columns:
    val = note_df.iloc[0]["package_contd"]
    if pd.notna(val): package_contents.append(val)
package_sorted = sort_content(package_contents)
package = '\n'.join(package_sorted) if package_sorted else ""


# ─────────────────────────────────────────────────────────────────────────────
# 2×2 그리드 레이아웃
# ─────────────────────────────────────────────────────────────────────────────
col11, col12 = st.columns(2)

with col11:
    st.subheader("📢 공지사항")
    if notice:
        formatted_notice = format_content_display(notice.split('\n'), "📣")
        for line in formatted_notice:
            st.markdown(line)
    else:
        st.info("공지사항이 없습니다")

with col12:
    st.subheader("📅 오늘의 일정")
    if schedule:
        formatted_schedule = format_content_display(schedule.split('\n'), "⏰")
        for line in formatted_schedule:
            st.markdown(line)
    else:
        st.info("오늘 일정이 없습니다")

col21, col22 = st.columns(2)

with col21:
    st.subheader("⚔️ 연맹대결")
    if duel_contd:
        formatted_duel = format_content_display(duel_contd.split('\n'), "🏆")
        for line in formatted_duel:
            st.markdown(line)
    else:
        st.info("연맹대결 일정이 없습니다")

with col22:
    st.subheader("📜 이벤트")
    if event:
        formatted_event = format_content_display(event.split('\n'), "🎯")
        for line in formatted_event:
            st.markdown(line)
    else:
        st.info("이벤트가 없습니다")
    if package:
        formatted_package = format_content_display(package.split('\n'), "💰")
        for line in formatted_package:
            st.markdown(line)
    else:
        st.info("이벤트가 없습니다")
        
         

# ─────────────────────────────────────────────────────────────────────────────
# 향후 7개 게임 일자 일정
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📅 향후 7개 게임 일자")

future_data = []
for i in range(1, 8):
    future_game_date = selected_date + timedelta(days=i)
    future_daily = daily_df.loc[daily_df["Date"] == pd.Timestamp(future_game_date)]
    
    lines = []
    if not future_daily.empty:
        if "timetable_daily" in future_daily.columns:
            val = future_daily.iloc[0]["timetable_daily"]
            if pd.notna(val):
                lines += [line.strip() for line in str(val).split('\n') if line.strip()]
        if "train_daily" in future_daily.columns:
            val = future_daily.iloc[0]["train_daily"]
            if pd.notna(val):
                lines += [line.strip() for line in str(val).split('\n') if line.strip()]
    
    lines = sorted(set(lines))
    event_text = ", ".join(lines) if lines else "일정 없음"
    
    future_data.append({
        "날짜": future_game_date.strftime("%m/%d"),
        "요일": ['월','화','수','목','금','토','일'][future_game_date.weekday()],
        "일정": event_text
    })

future_df = pd.DataFrame(future_data)
st.dataframe(future_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# 전체 내용 클립보드 복사
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📋 전체 내용 복사")

# 복사할 전체 텍스트 생성
all_text = f"""📢 공지사항
{notice if notice else "공지사항이 없습니다"}

📅 오늘의 일정 ({selected_date:%Y년 %m월 %d일} {['월','화','수','목','금','토','일'][weekday-1]}요일)
{schedule if schedule else "오늘 일정이 없습니다"}

🏆 연맹대결
{duel_contd if duel_contd else "연맹대결 일정이 없습니다"}

📜 이벤트
{event if event else "이벤트가 없습니다"}
"""

# 안전한 클립보드 복사 버튼
copy_js = f"""
<script>
async function copyToClipboard() {{
    const text = `{all_text.replace('`', '\\`').replace('$', '\\$')}`;
    try {{
        await navigator.clipboard.writeText(text);
        document.getElementById('copy-status').innerHTML = '✅ 복사 완료!';
        document.getElementById('copy-status').style.color = '#28a745';
        setTimeout(() => {{
            document.getElementById('copy-status').innerHTML = '';
        }}, 3000);
    }} catch (err) {{
        document.getElementById('copy-status').innerHTML = '❌ 복사 실패';
        document.getElementById('copy-status').style.color = '#dc3545';
    }}
}}
</script>
<div style="text-align: center; margin: 20px 0;">
    <button onclick="copyToClipboard()" style="
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
        📋 전체 내용 복사하기
    </button>
    <div id="copy-status" style="margin-top: 10px; font-weight: bold;"></div>
</div>
"""

st.markdown(copy_js, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 사이드바 메뉴
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.divider()
    st.header("🔧 툴박스 메뉴")
    
    selected_tool = st.selectbox(
        "계산기 선택",
        [
            "단위 계산기", "연맹대전 계산기", "군비 보상 계산기",
            "영웅 경험치 계산기", "영웅 장비 계산기", "스킬 강화 계산기"
        ]
    )
    
    if selected_tool:
        st.info(f"선택된 도구: **{selected_tool}**")
        st.write("🚧 개발 예정")

    # R4참고 메뉴 (GitHub Secrets 활용)
    st.divider()
    st.header("🔒 R4참고")
    
    if "r4_authenticated" not in st.session_state:
        st.session_state.r4_authenticated = False
    
    if not st.session_state.r4_authenticated:
        password = st.text_input("비밀번호 입력", type="password", key="r4_password")
        if st.button("접속"):
            # GitHub Secrets에서 비밀번호 확인
            correct_password = get_secret("R4_PWD", "r4password")
            if password == correct_password:
                st.session_state.r4_authenticated = True
                st.success("✅ 접근 승인")
                st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다")
    else:
        st.success("✅ R4 모드 활성화")
        if st.button("로그아웃"):
            st.session_state.r4_authenticated = False
            st.rerun()
        
        st.write("📋 R4 전용 내용")
        if not note_df.empty and "R45_contd" in note_df.columns:
            r4_content = note_df.iloc[0]["R45_contd"]
            if pd.notna(r4_content):
                st.write(r4_content)
            else:
                st.info("R4 참고 내용이 없습니다")
        else:
            st.info("R4 데이터가 없습니다")

    # 통계 정보
    st.divider()
    st.header("📊 통계")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("일정 항목", len(schedule.split('\n')) if schedule else 0)
    with col_stat2:
        st.metric("이벤트 항목", len(event.split('\n')) if event else 0)

# ─────────────────────────────────────────────────────────────────────────────
# 디버그 정보 (개선)
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🔍 디버그 정보"):
    debug_cols = st.columns(2)
    
    with debug_cols[0]:
        st.write("**날짜 정보**")
        st.json({
            "선택된 게임 일자": str(selected_date),
            "요일": weekday,
            "주차 인덱스": week_index,
            "오늘과의 차이": (selected_date - game_day).days
        })
    
    with debug_cols[1]:
        st.write("**데이터 상태**")
        st.json({
            "일일 데이터": len(daily_df),
            "주간 데이터": len(weekly_df),
            "월간 데이터": len(monthly_df),
            "공지사항 항목": len(notice_sorted),
            "일정 항목": len(schedule_sorted),
            "연맹대전 항목": len(duel_sorted),
            "이벤트 항목": len(event_sorted)
        })

# 푸터
st.divider()
st.markdown(
    f"""
    <div style='text-align: center; color: #666; font-size: 12px; margin: 20px 0;'>
        🎮 LAST WAR:SURVIVAL PZTK #777 연맹 대시보드 v3.0<br>
        Made with ❤️ by @고체RHCP | Powered by Streamlit<br>
        최종 업데이트: {kst_now.strftime('%Y-%m-%d %H:%M:%S KST')}
    </div>
    """, 
    unsafe_allow_html=True
)
