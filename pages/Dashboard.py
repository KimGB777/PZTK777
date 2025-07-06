# pages/Dashboard.py

import streamlit as st  # type: ignore
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.data_extract import extract_section, format_content_display
from components.copy_button import render_copy_button
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 한국 시간대
KST = timezone(timedelta(hours=9))

def kst_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(KST)

def safe_extract_section(df_map: dict, cols: list, name: str) -> list:
    """안전한 섹션 추출"""
    try:
        return extract_section(df_map, cols)
    except Exception as e:
        logger.error(f"{name} 추출 오류: {e}")
        return [f"{name} 데이터 없음"]

def render_section(title: str, lines: list, icon: str):
    """섹션 렌더링"""
    st.subheader(title)
    if lines and "데이터 없음" not in lines[0]:
        for line in format_content_display(lines, icon):
            st.markdown(line)
    else:
        st.markdown(f"{icon} {title}이(가) 없습니다.")

def render(load_sheet):
    """대시보드 페이지 렌더링"""
    try:
        st.title("🏠 대시보드")

        # 날짜 선택
        now = kst_now()
        default_day = (now - timedelta(days=1)).date() if now.hour < 11 else now.date()
        game_day = st.date_input("날짜 선택", value=default_day, key="dashboard_date")

        # 데이터 로드
        with st.spinner("📊 데이터 로딩 중..."):
            daily = load_sheet("daily")
            weekly = load_sheet("weekly")
            monthly = load_sheet("monthly")
            note = load_sheet("note")

            if not any(df.empty for df in [daily, weekly, monthly, note]):
                st.success("✅ 모든 데이터 로드 완료")
            else:
                st.warning("⚠️ 일부 데이터 로드 실패 - 사용 가능한 데이터로 진행")

        # 날짜 기반 필터링
        daily["Date"] = pd.to_datetime(daily["Date"])
        wd = game_day.isoweekday()
        wi = (game_day.isocalendar().week - 1) % 4
        d_daily = daily[daily["Date"] == pd.Timestamp(game_day)]
        d_weekly = weekly[weekly["weekday"] == wd] if "weekday" in weekly.columns else pd.DataFrame()
        d_monthly = monthly[monthly["mod(weeknum,4)"] == wi] if "mod(weeknum,4)" in monthly.columns else pd.DataFrame()

        # 섹션별 데이터 추출
        notice = safe_extract_section(
            {"notice_weekly": d_weekly, "notice_daily": d_daily, "notice_contd": note},
            ["notice_weekly", "notice_daily", "notice_contd"], "공지사항"
        )
        schedule = safe_extract_section(
            {"schedule_weekly": d_weekly, "schedule_daily": d_daily, "schedule_contd": note},
            ["schedule_weekly", "schedule_daily", "schedule_contd"], "일정"
        )
        duel = safe_extract_section(
            {"duel_weekly": d_weekly, "duel_daily": d_daily, "duel_contd": note},
            ["duel_weekly", "duel_daily", "duel_contd"], "연맹대결"
        )
        event = safe_extract_section(
            {"event_weekly": d_weekly, "event_daily": d_daily, "event_contd": note, "event_monthly": d_monthly},
            ["event_weekly", "event_daily", "event_contd", "event_monthly"], "이벤트"
        )
        package = safe_extract_section(
            {"package_weekly": d_weekly, "package_daily": d_daily, "package_contd": note, "package_monthly": d_monthly},
            ["package_weekly", "package_daily", "package_contd", "package_monthly"], "패키지"
        )

        # 2x2 그리드 레이아웃
        col1, col2 = st.columns(2)
        with col1:
            render_section("📢 공지사항", notice, "📣")
        with col2:
            render_section("📅 오늘 일정", schedule, "⏰")

        col3, col4 = st.columns(2)
        with col3:
            render_section("⚔️ 연맹대결", duel, "🏆")
        with col4:
            render_section("📜 이벤트", event, "🎯")
            render_section("💰 패키지", package, "💰")

        st.divider()

        # 향후 7일 캘린더 
        st.subheader("📅 다음 7일 일정")
        weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
        dates = [game_day + timedelta(days=i) for i in range(1, 8)]

        # 7일을 1행으로 배치
        calendar_data = []
        week_data = []
        
        for idx, fd in enumerate(dates):
            df_f = daily[daily["Date"] == pd.Timestamp(fd)]
            wd2 = fd.isoweekday()
            wi2 = (fd.isocalendar().week - 1) % 4
            df_w = weekly[weekly["weekday"] == wd2] if "weekday" in weekly.columns else pd.DataFrame()
            df_m = monthly[monthly["mod(weeknum,4)"] == wi2] if "mod(weeknum,4)" in monthly.columns else pd.DataFrame()

            items = []
            def add_item(label, key, df_src):
                lines = safe_extract_section({key: df_src}, [key], key)
                if lines and "데이터 없음" not in lines[0]:
                    items.extend(f"{label}: {line}" for line in lines if line.strip())

            # 한글 라벨로 출력
            add_item("일정", "schedule_daily", df_f)
            add_item("일정", "schedule_weekly", df_w)
            add_item("일정", "schedule_monthly", df_m)
            add_item("공지", "notice_daily", df_f)
            add_item("열차", "train_daily", df_f)
            add_item("훈련", "excercise_daily", df_f)

            header = f"{fd:%m/%d}({weekday_kr[fd.weekday()]})"
            content = "\n".join(items) if items else "-"
            week_data.append(f"**{header}**\n{content}")

        calendar_data.append(week_data)

        # DataFrame으로 표 생성
        cal_df = pd.DataFrame(
            calendar_data,
            index=weekday_kr,
            columns=["다음 주"]
        )
        st.dataframe(cal_df, use_container_width=True)
        st.divider()


        st.divider()

        # 전체 내용 복사
        st.subheader("📋 전체 내용 복사")
        all_parts = []
        for title, lines, icon in [
            ("공지사항", notice, "📢"),
            ("오늘 일정", schedule, "📅"),
            ("연맹대결", duel, "⚔️"),
            ("이벤트", event, "📜"),
            ("패키지", package, "💰")
        ]:
            if lines and "데이터 없음" not in lines[0]:
                all_parts += [f"{icon} {title}"] + lines + [""]

        all_text = "\n".join(all_parts) or "복사할 내용이 없습니다."
        render_copy_button(all_text)

        with st.expander("📄 복사 내용 미리보기"):
            st.text(all_text)

        # 새로고침 버튼
        if st.button("🔄 데이터 새로고침"):
            st.cache_data.clear()
            st.rerun()

    except Exception as e:
        logger.error(f"Dashboard 렌더링 오류: {e}")
        st.error("대시보드 로드 중 오류가 발생했습니다.")
        if st.checkbox("🔧 디버그 정보 표시"):
            st.code(str(e))

if __name__ == "__main__":
    render(lambda x: pd.DataFrame())

