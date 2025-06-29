# pages/Dashboard.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.gsheet_loader import logad_gsheet_data
from utils.data_loader import load_event_data
from utils.data_extract import extract_section, format_content_display
from components.copy_button import render_copy_button

# KST 시간대 정의
KST = timezone(timedelta(hours=9))
def get_kst_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(KST)

def render():
    st.title("🏠대시보드")
    # ─────────────────────────────────────────────────────────────────────────
    # 날짜 설정 UI (KST 11:00~익일 11:00)
    # ─────────────────────────────────────────────────────────────────────────
    kst_now = get_kst_now()
    default_day = (kst_now - timedelta(days=1)).date() if kst_now.hour < 11 else kst_now.date()

    with st.info("📅 일자 선택 (한국 시간 11:00~익일 11:00)"):
        game_day = st.date_input(
            label="날짜 입력 (한국 시간 11:00~익일11:00 이후를 당일로 간주합니)",
            value=default_day,
            help="한국 시간으로 11:00 이후를 당일로 간주합니다."
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 데이터 로드 및 필터링
    # ─────────────────────────────────────────────────────────────────────────
    DATA_FILE = "data/data_250628_test.xlsx"
    daily_df, weekly_df, monthly_df, note_df = load_event_data(DATA_FILE)

    wd = game_day.isoweekday()
    wi = (game_day.isocalendar().week - 1) % 4

    today_daily   = daily_df[daily_df["Date"] == pd.Timestamp(game_day)]
    today_weekly  = weekly_df[weekly_df["weekday"] == wd]
    today_monthly = monthly_df[monthly_df["mod(weeknum,4)"] == wi]

    # ─────────────────────────────────────────────────────────────────────────
    # 섹션별 추출 및 출력
    # ─────────────────────────────────────────────────────────────────────────
    notice_lines = extract_section({
        "notice_weekly": today_weekly,
        "notice_daily":  today_daily,
        "notice_contd":  note_df
    }, ["notice_weekly", "notice_daily", "notice_contd"])
    schedule_lines = extract_section({
        **{c: today_weekly for c in ["schedule_weekly"]},
        **{c: today_daily  for c in ["schedule_daily", "train_daily", "zombie_daily", "excercise_daily"]},
        "schedule_contd": note_df
    }, ["schedule_weekly","schedule_daily","schedule_contd","train_daily","zombie_daily","excercise_daily"])
    duel_lines = extract_section({
        **{c: today_weekly for c in ["duel_weekly"]},
        **{c: today_daily  for c in ["duel_daily"]},
        "duel_contd": note_df
    }, ["duel_weekly","duel_daily","duel_contd"])
    event_lines = extract_section({
        **{c: today_weekly   for c in ["event_weekly"]},
        **{c: today_daily    for c in ["event_daily"]},
        "event_contd": note_df,
        "event_monthly": today_monthly
    }, ["event_weekly","event_daily","event_contd","event_monthly"])
    package_lines = extract_section({
        **{c: today_weekly   for c in ["package_weekely"]},
        **{c: today_daily    for c in ["package_daily"]},
        "package_contd": note_df,
        "package_monthly": today_monthly
    }, ["package_weekely","package_daily","package_contd","package_monthly"])

    # 2×2 레이아웃
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📢 공지사항")
        if notice_lines:
            for line in format_content_display(notice_lines, "📣"):
                st.markdown(line)
        else:
            st.info("공지사항이 없습니다")
    with c2:
        st.subheader("📅 오늘 일정")
        if schedule_lines:
            for line in format_content_display(schedule_lines, "⏰"):
                st.markdown(line)
        else:
            st.info("오늘 일정이 없습니다")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("⚔️ 연맹대결")
        if duel_lines:
            for line in format_content_display(duel_lines, "🏆"):
                st.markdown(line)
        else:
            st.info("연맹대결 일정이 없습니다")
    with c4:
        st.subheader("📜 이벤트")
        if event_lines:
            for line in format_content_display(event_lines, "🎯"):
                st.markdown(line)
        else:
            st.info("이벤트가 없습니다")
        if package_lines:
            for line in format_content_display(package_lines, "💰"):
                st.markdown(line)

    # 향후 7일 일정
    st.subheader("📅 향후 7일 일정")
    for i in range(1, 8):
        d = game_day + timedelta(days=i)
        df = daily_df[daily_df["Date"] == pd.Timestamp(d)]
        future = extract_section({"schedule_daily": df, "train_daily": df}, ["schedule_daily","train_daily"])
        text = ", ".join(future) if future else "일정 없음"
        st.write(f"{d:%m/%d (%a)} → {text}")

    # 전체 복사 버튼
    all_text = "\n".join([
        "📢 공지사항", *notice_lines, "",
        "📅 오늘 일정", *schedule_lines, "",
        "⚔️ 연맹대결", *duel_lines, "",
        "📜 이벤트", *event_lines, "",
        "💰 패키지", *package_lines
    ])
    st.subheader("📋 전체 내용 복사")
    render_copy_button(all_text)
