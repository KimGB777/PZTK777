# pages/Dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.gsheet_loader import load_gsheet_data
from utils.data_extract import extract_section, format_content_display
from components.copy_button import render_copy_button
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

def kst_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(KST)

def safe_extract_section(df_map: dict, columns: list, section_name: str) -> list:
    """안전한 섹션 추출 (에러 핸들링 포함)"""
    try:
        return extract_section(df_map, columns)
    except Exception as e:
        logger.error(f"{section_name} 섹션 추출 오류: {e}")
        return [f"{section_name} 데이터를 불러올 수 없습니다."]

def get_fallback_data() -> dict:
    """데이터 로드 실패 시 기본 데이터 반환"""
    return {
        "daily": pd.DataFrame(),
        "weekly": pd.DataFrame(),
        "monthly": pd.DataFrame(),
        "note": pd.DataFrame()
    }

def render() -> None:
    st.title("🏠 대시보드")
    
    try:
        # 날짜 선택 UI
        now = kst_now()
        default_day = (now - timedelta(days=1)).date() if now.hour < 11 else now.date()
        
        with st.container():
            st.info("📅 일자 선택 (한국 시간 11:00~익일 11:00 기준으로 반영됩니다.)")
            game_day = st.date_input(
                label="날짜 입력",
                value=default_day,
                key="dashboard_date"
            )
        
        # 데이터 로드 시도
        with st.spinner("📊 데이터를 불러오는 중..."):
            try:
                dfs = load_gsheet_data()
                data_loaded = True
                st.success("✅ 데이터 로드 완료")
            except Exception as e:
                logger.error(f"데이터 로드 실패: {e}")
                st.error("⚠️ 데이터를 불러올 수 없습니다. 기본 모드로 전환합니다.")
                dfs = get_fallback_data()
                data_loaded = False
        
        if not data_loaded:
            st.warning("현재 Google Sheets 연결에 문제가 있습니다. 관리자에게 문의해주세요.")
            return
        
        # 데이터 추출
        daily, weekly, monthly, note = dfs["daily"], dfs["weekly"], dfs["monthly"], dfs["note"]
        
        # 날짜 관련 계산
        wd = game_day.isoweekday()  # 1=월요일, 7=일요일
        wi = (game_day.isocalendar().week - 1) % 4  # 4주 주기
        
        # 데이터 필터링
        try:
            if not daily.empty and "Date" in daily.columns:
                d_daily = daily[daily["Date"] == pd.Timestamp(game_day)]
            else:
                d_daily = pd.DataFrame()
            
            if not weekly.empty and "weekday" in weekly.columns:
                d_weekly = weekly[weekly["weekday"] == wd]
            else:
                d_weekly = pd.DataFrame()
            
            if not monthly.empty and "mod(weeknum,4)" in monthly.columns:
                d_month = monthly[monthly["mod(weeknum,4)"] == wi]
            else:
                d_month = pd.DataFrame()
        except Exception as e:
            logger.error(f"데이터 필터링 오류: {e}")
            st.error("데이터 필터링 중 오류가 발생했습니다.")
            return
        
        # 섹션별 데이터 추출
        try:
            # 공지사항
            notice_lines = safe_extract_section({
                "notice_weekly": d_weekly,
                "notice_daily": d_daily,
                "notice_contd": note
            }, ["notice_weekly", "notice_daily", "notice_contd"], "공지사항")
            
            # 일정
            schedule_lines = safe_extract_section({
                **{c: d_weekly for c in ["schedule_weekly"]},
                **{c: d_daily for c in ["schedule_daily", "train_daily", "zombie_daily", "excercise_daily"]},
                "schedule_contd": note
            }, ["schedule_weekly", "schedule_daily", "schedule_contd",
                "train_daily", "zombie_daily", "excercise_daily"], "일정")
            
            # 연맹대결
            duel_lines = safe_extract_section({
                **{c: d_weekly for c in ["duel_weekly"]},
                **{c: d_daily for c in ["duel_daily"]},
                "duel_contd": note
            }, ["duel_weekly", "duel_daily", "duel_contd"], "연맹대결")
            
            # 이벤트
            event_lines = safe_extract_section({
                **{c: d_weekly for c in ["event_weekly"]},
                **{c: d_daily for c in ["event_daily"]},
                "event_contd": note,
                "event_monthly": d_month
            }, ["event_weekly", "event_daily", "event_contd", "event_monthly"], "이벤트")
            
            # 패키지
            package_lines = safe_extract_section({
                **{c: d_weekly for c in ["package_weekely"]},  # 오타 유지 (원본과 호환성)
                **{c: d_daily for c in ["package_daily"]},
                "package_contd": note,
                "package_monthly": d_month
            }, ["package_weekely", "package_daily", "package_contd", "package_monthly"], "패키지")
            
        except Exception as e:
            logger.error(f"섹션 데이터 추출 오류: {e}")
            st.error("데이터 처리 중 오류가 발생했습니다.")
            return
        
        # UI 렌더링 - 2x2 그리드
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📢 공지사항")
            if notice_lines:
                for line in format_content_display(notice_lines, "📣"):
                    st.markdown(line)
            else:
                st.markdown("📣 공지사항이 없습니다.")
        
        with col2:
            st.subheader("📅 오늘 일정")
            if schedule_lines:
                for line in format_content_display(schedule_lines, "⏰"):
                    st.markdown(line)
            else:
                st.markdown("⏰ 오늘 일정이 없습니다.")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("⚔️ 연맹대결")
            if duel_lines:
                for line in format_content_display(duel_lines, "🏆"):
                    st.markdown(line)
            else:
                st.markdown("🏆 연맹대결 일정이 없습니다.")
        
        with col4:
            st.subheader("📜 이벤트 & 패키지")
            
            # 이벤트
            if event_lines:
                for line in format_content_display(event_lines, "🎯"):
                    st.markdown(line)
            else:
                st.markdown("🎯 이벤트가 없습니다.")
            
            # 패키지
            if package_lines:
                for line in format_content_display(package_lines, "💰"):
                    st.markdown(line)
        
        st.divider()
        
        # 향후 7일 일정
        st.subheader("📅 향후 7일 일정")
        
        try:
            future_schedule = []
            for i in range(1, 8):
                future_date = game_day + timedelta(days=i)
                
                if not daily.empty and "Date" in daily.columns:
                    df_future = daily[daily["Date"] == pd.Timestamp(future_date)]
                    future_events = safe_extract_section(
                        {"schedule_daily": df_future, "train_daily": df_future},
                        ["schedule_daily", "train_daily"],
                        f"{future_date} 일정"
                    )
                    
                    # 요일 한글 변환
                    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
                    weekday_name = weekday_kr[future_date.weekday()]
                    
                    events_text = ", ".join(future_events) if future_events and future_events != [f"{future_date} 일정 데이터를 불러올 수 없습니다."] else "일정 없음"
                    future_schedule.append(f"**{future_date.strftime('%m/%d')} ({weekday_name})** → {events_text}")
                else:
                    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
                    weekday_name = weekday_kr[future_date.weekday()]
                    future_schedule.append(f"**{future_date.strftime('%m/%d')} ({weekday_name})** → 일정 없음")
            
            for schedule_item in future_schedule:
                st.markdown(schedule_item)
                
        except Exception as e:
            logger.error(f"향후 일정 생성 오류: {e}")
            st.error("향후 일정을 불러올 수 없습니다.")
        
        st.divider()
        
        # 전체 내용 복사 기능
        st.subheader("📋 전체 내용 복사")
        
        try:
            all_text_parts = []
            
            if notice_lines and notice_lines != ["공지사항 데이터를 불러올 수 없습니다."]:
                all_text_parts.extend(["📢 공지사항"] + notice_lines + [""])
            
            if schedule_lines and schedule_lines != ["일정 데이터를 불러올 수 없습니다."]:
                all_text_parts.extend(["📅 오늘 일정"] + schedule_lines + [""])
            
            if duel_lines and duel_lines != ["연맹대결 데이터를 불러올 수 없습니다."]:
                all_text_parts.extend(["⚔️ 연맹대결"] + duel_lines + [""])
            
            if event_lines and event_lines != ["이벤트 데이터를 불러올 수 없습니다."]:
                all_text_parts.extend(["📜 이벤트"] + event_lines + [""])
            
            if package_lines and package_lines != ["패키지 데이터를 불러올 수 없습니다."]:
                all_text_parts.extend(["💰 패키지"] + package_lines + [""])
            
            all_text = "\n".join(all_text_parts) if all_text_parts else "복사할 내용이 없습니다."
            
            # 복사 버튼 렌더링
            render_copy_button(all_text)
            
            # 텍스트 미리보기
            with st.expander("📄 복사 내용 미리보기"):
                st.text(all_text)
                
        except Exception as e:
            logger.error(f"복사 기능 오류: {e}")
            st.error("복사 기능에 오류가 발생했습니다.")
        
        # 데이터 현황
        with st.expander("📊 데이터 현황"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("일일 데이터", len(daily) if not daily.empty else 0)
            with col2:
                st.metric("주간 데이터", len(weekly) if not weekly.empty else 0)
            with col3:
                st.metric("월간 데이터", len(monthly) if not monthly.empty else 0)
            with col4:
                st.metric("메모 데이터", len(note) if not note.empty else 0)
        
        # 자동 새로고침 기능
        if st.button("🔄 데이터 새로고침"):
            st.cache_data.clear()  # 캐시 클리어
            st.rerun()
            
    except Exception as e:
        logger.error(f"Dashboard 렌더링 오류: {e}")
        st.error("대시보드를 불러오는 중 오류가 발생했습니다.")
        st.info("페이지를 새로고침하거나 관리자에게 문의해주세요.")
        
        # 에러 디버깅 정보 (개발 모드에서만)
        if st.checkbox("🔧 디버그 정보 표시"):
            st.code(str(e))
