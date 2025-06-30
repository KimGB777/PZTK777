#pages/Calculator.py
'''
import streamlit as st

def render() -> None:
    st.title("🖩 계산기")
    tool = st.selectbox("계산기 종류", [
        "영웅 경험치", "영웅 스킬훈장", "영웅 전속",
        "장비 업그레이드", "소요 시간"
    ])
    st.info(f"선택된 계산기: {tool}")
    
        # 각 계산기 로직 분기
    if tool == "영웅 경험치":
        # 예시 입력·결과
        lvl = st.number_input("현재 레벨", 1, 100, 1)
        exp = st.number_input("필요 경험치", 0, 100000, 1000)
        st.write(f"목표까지 남은 경험치: {exp - lvl * 100}")
    # … 나머지 계산기 구현 …
    # TODO: implement specific calculators
'''    
    
# pages/Calculator.py
import streamlit as st
import math

def calculate_hero_exp(current_level: int, target_level: int) -> dict:
    """영웅 경험치 계산"""
    if target_level <= current_level:
        return {"error": "목표 레벨이 현재 레벨보다 높아야 합니다."}
    
    # 라스트워 영웅 경험치 공식 (예시)
    exp_per_level = lambda lvl: int(lvl * 100 + (lvl ** 1.5) * 50)
    
    total_exp_needed = 0
    for level in range(current_level, target_level):
        total_exp_needed += exp_per_level(level)
    
    return {
        "total_exp": total_exp_needed,
        "levels_to_go": target_level - current_level,
        "avg_exp_per_level": total_exp_needed // (target_level - current_level)
    }

def calculate_hero_skill_medals(current_skill: int, target_skill: int) -> dict:
    """영웅 스킬훈장 계산"""
    if target_skill <= current_skill:
        return {"error": "목표 스킬레벨이 현재보다 높아야 합니다."}
    
    # 스킬훈장 공식 (예시)
    medals_per_level = lambda lvl: int(lvl * 10 + (lvl ** 2) * 2)
    
    total_medals = 0
    for level in range(current_skill, target_skill):
        total_medals += medals_per_level(level)
    
    return {
        "total_medals": total_medals,
        "skill_levels_to_go": target_skill - current_skill
    }

def calculate_equipment_upgrade(current_grade: int, target_grade: int, item_type: str) -> dict:
    """장비 업그레이드 계산"""
    if target_grade <= current_grade:
        return {"error": "목표 등급이 현재보다 높아야 합니다."}
    
    # 장비별 업그레이드 비용 (예시)
    base_costs = {
        "무기": 1000,
        "방어구": 800,
        "액세서리": 600
    }
    
    base_cost = base_costs.get(item_type, 1000)
    total_cost = 0
    
    for grade in range(current_grade, target_grade):
        cost = int(base_cost * (1.5 ** grade))
        total_cost += cost
    
    return {
        "total_cost": total_cost,
        "grades_to_go": target_grade - current_grade,
        "item_type": item_type
    }

def calculate_time_requirement(activity: str, target_amount: int) -> dict:
    """소요 시간 계산"""
    # 활동별 시간 (분 단위)
    time_per_unit = {
        "자원 채집": 2,
        "몬스터 사냥": 5,
        "던전 클리어": 15,
        "연맹 임무": 30
    }
    
    unit_time = time_per_unit.get(activity, 5)
    total_minutes = target_amount * unit_time
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    return {
        "total_minutes": total_minutes,
        "hours": hours,
        "minutes": minutes,
        "activity": activity
    }

def render() -> None:
    """Calculator 페이지 렌더링"""
    st.title("🖩 계산기")
    
    # 계산기 종류 선택
    tool = st.selectbox("계산기 종류", [
        "영웅 경험치", "영웅 스킬훈장", "영웅 전속",
        "장비 업그레이드", "소요 시간"
    ])
    
    st.info(f"선택된 계산기: {tool}")
    
    # 각 계산기 로직 분기 (FIXED: calc -> tool)
    if tool == "영웅 경험치":
        st.subheader("📈 영웅 경험치 계산기")
        
        col1, col2 = st.columns(2)
        with col1:
            current_lvl = st.number_input("현재 레벨", min_value=1, max_value=999, value=1)
        with col2:
            target_lvl = st.number_input("목표 레벨", min_value=1, max_value=999, value=10)
        
        if st.button("계산하기", key="exp_calc"):
            result = calculate_hero_exp(current_lvl, target_lvl)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("계산 완료!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("필요 총 경험치", f"{result['total_exp']:,}")
                with col2:
                    st.metric("레벨 차이", result['levels_to_go'])
                with col3:
                    st.metric("평균 경험치/레벨", f"{result['avg_exp_per_level']:,}")
    
    elif tool == "영웅 스킬훈장":
        st.subheader("🏅 영웅 스킬훈장 계산기")
        
        col1, col2 = st.columns(2)
        with col1:
            current_skill = st.number_input("현재 스킬 레벨", min_value=0, max_value=100, value=0)
        with col2:
            target_skill = st.number_input("목표 스킬 레벨", min_value=0, max_value=100, value=10)
        
        if st.button("계산하기", key="skill_calc"):
            result = calculate_hero_skill_medals(current_skill, target_skill)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("계산 완료!")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("필요 총 훈장", f"{result['total_medals']:,}")
                with col2:
                    st.metric("스킬 레벨 차이", result['skill_levels_to_go'])
    
    elif tool == "영웅 전속":
        st.subheader("⚡ 영웅 전속 계산기")
        st.info("🚧 개발 중입니다. 곧 업데이트 예정!")
        
        # 간단한 전속 계산 UI
        attack_speed = st.slider("현재 공격 속도", 0.1, 5.0, 1.0, 0.1)
        target_speed = st.slider("목표 공격 속도", 0.1, 5.0, 2.0, 0.1)
        
        speed_increase = ((target_speed - attack_speed) / attack_speed) * 100
        st.metric("속도 증가율", f"{speed_increase:.1f}%")
    
    elif tool == "장비 업그레이드":
        st.subheader("⚔️ 장비 업그레이드 계산기")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            item_type = st.selectbox("장비 종류", ["무기", "방어구", "액세서리"])
        with col2:
            current_grade = st.number_input("현재 등급", min_value=0, max_value=20, value=0)
        with col3:
            target_grade = st.number_input("목표 등급", min_value=0, max_value=20, value=5)
        
        if st.button("계산하기", key="equip_calc"):
            result = calculate_equipment_upgrade(current_grade, target_grade, item_type)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("계산 완료!")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("필요 총 비용", f"{result['total_cost']:,}")
                with col2:
                    st.metric("등급 차이", result['grades_to_go'])
    
    elif tool == "소요 시간":
        st.subheader("⏰ 소요 시간 계산기")
        
        col1, col2 = st.columns(2)
        with col1:
            activity = st.selectbox("활동 종류", [
                "자원 채집", "몬스터 사냥", "던전 클리어", "연맹 임무"
            ])
        with col2:
            target_amount = st.number_input("목표 횟수", min_value=1, max_value=10000, value=10)
        
        if st.button("계산하기", key="time_calc"):
            result = calculate_time_requirement(activity, target_amount)
            st.success("계산 완료!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 소요시간", f"{result['hours']}시간 {result['minutes']}분")
            with col2:
                st.metric("총 분", f"{result['total_minutes']}분")
            with col3:
                st.metric("활동", result['activity'])
    
    # 도움말
    with st.expander("📖 계산기 사용법"):
        st.markdown("""
        ### 🎯 각 계산기 설명
        
        **영웅 경험치**: 현재 레벨에서 목표 레벨까지 필요한 총 경험치를 계산합니다.
        
        **영웅 스킬훈장**: 스킬 레벨 업그레이드에 필요한 훈장 수를 계산합니다.
        
        **영웅 전속**: 공격 속도 증가율을 계산합니다. (개발 중)
        
        **장비 업그레이드**: 장비 등급 업그레이드에 필요한 총 비용을 계산합니다.
        
        **소요 시간**: 특정 활동을 목표 횟수만큼 수행하는데 걸리는 시간을 계산합니다.
        
        ### ⚠️ 주의사항
        - 모든 계산은 예상치이며 실제 게임과 다를 수 있습니다.
        - 게임 업데이트에 따라 수치가 변경될 수 있습니다.
        """)
