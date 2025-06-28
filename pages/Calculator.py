import streamlit as st

def render():
    st.title("🧮 계산기")
    # 계산기 종류 선택
    calc = st.selectbox("계산기 선택", [
        "영웅 경험치", "영웅 스킬훈장", "영웅 전속",
        "장비 업그레이드", "소요 시간"
    ])
    st.markdown(f"**선택된 계산기:** {calc}")
    # 각 계산기 로직 분기
    if calc == "영웅 경험치":
        # 예시 입력·결과
        lvl = st.number_input("현재 레벨", 1, 100, 1)
        exp = st.number_input("필요 경험치", 0, 100000, 1000)
        st.write(f"목표까지 남은 경험치: {exp - lvl * 100}")
    # … 나머지 계산기 구현 …
