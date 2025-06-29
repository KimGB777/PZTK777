# pages/Dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.gsheet_loader import load_gsheet_data
from utils.data_extract import extract_section, format_content_display
from components.copy_button import render_copy_button

KST = timezone(timedelta(hours=9))
def kst_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(KST)

def render() -> None:
    st.title("🏠 대시보드")

    # Date picker inside Dashboard
    now = kst_now()
    default_day = (now - timedelta(days=1)).date() if now.hour < 11 else now.date()
    with st.info("📅 일자 선택 (한국 시간 11:00~익일 11:00)"):
        game_day = st.date_input(
            label="날짜 입력 (한국 시간 11:00~익일11:00 이후를 당일로 간주합니)",
            value=default_day,
            help="한국 시간으로 11:00 이후를 당일로 간주합니다."
        )
    # Load from Google Sheets
    dfs = load_gsheet_data()
    daily, weekly, monthly, note = dfs["daily"], dfs["weekly"], dfs["monthly"], dfs["note"]

    wd = game_day.isoweekday()
    wi = (game_day.isocalendar().week - 1) % 4
    d_daily  = daily[daily["Date"] == pd.Timestamp(game_day)]
    d_weekly = weekly[weekly["weekday"] == wd]
    d_month  = monthly[monthly["mod(weeknum,4)"] == wi]

    # Extract sections
    notice_lines = extract_section({
        "notice_weekly": d_weekly,
        "notice_daily":  d_daily,
        "notice_contd":  note
    }, ["notice_weekly","notice_daily","notice_contd"])

    schedule_lines = extract_section({
        **{c: d_weekly for c in ["schedule_weekly"]},
        **{c: d_daily  for c in ["schedule_daily","train_daily","zombie_daily","excercise_daily"]},
        "schedule_contd": note
    }, ["schedule_weekly","schedule_daily","schedule_contd",
        "train_daily","zombie_daily","excercise_daily"])

    duel_lines = extract_section({
        **{c: d_weekly for c in ["duel_weekly"]},
        **{c: d_daily  for c in ["duel_daily"]},
        "duel_contd": note
    }, ["duel_weekly","duel_daily","duel_contd"])

    event_lines = extract_section({
        **{c: d_weekly for c in ["event_weekly"]},
        **{c: d_daily  for c in ["event_daily"]},
        "event_contd":  note,
        "event_monthly": d_month
    }, ["event_weekly","event_daily","event_contd","event_monthly"])

    package_lines = extract_section({
        **{c: d_weekly for c in ["package_weekely"]},
        **{c: d_daily  for c in ["package_daily"]},
        "package_contd":   note,
        "package_monthly": d_month
    }, ["package_weekely","package_daily","package_contd","package_monthly"])

    # 2×2 grid display
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📢 공지사항")
        for ln in format_content_display(notice_lines, "📣") or ["공지사항이 없습니다"]:
            st.markdown(ln)
    with c2:
        st.subheader("📅 오늘 일정")
        for ln in format_content_display(schedule_lines, "⏰") or ["오늘 일정이 없습니다"]:
            st.markdown(ln)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("⚔️ 연맹대결")
        for ln in format_content_display(duel_lines, "🏆") or ["연맹대결 일정이 없습니다"]:
            st.markdown(ln)
    with c4:
        st.subheader("📜 이벤트")
        for ln in format_content_display(event_lines, "🎯") or ["이벤트가 없습니다"]:
            st.markdown(ln)
        for ln in format_content_display(package_lines, "💰"):
            st.markdown(ln)

    # Next 7 days
    st.subheader("📅 향후 7일 일정")
    for i in range(1, 8):
        d = game_day + timedelta(days=i)
        df = daily[daily["Date"] == pd.Timestamp(d)]
        fut = extract_section({"schedule_daily": df, "train_daily": df},
                               ["schedule_daily","train_daily"])
        st.write(f"{d:%m/%d (%a)} → {', '.join(fut) if fut else '일정 없음'}")

    # Copy all text
    all_text = "\n".join(
        ["📢 공지사항"] + notice_lines +
        ["", "📅 오늘 일정"] + schedule_lines +
        ["", "⚔️ 연맹대결"] + duel_lines +
        ["", "📜 이벤트"] + event_lines +
        ["", "💰 패키지"] + package_lines
    )
    st.subheader("📋 전체 내용 복사")
    render_copy_button(all_text)
