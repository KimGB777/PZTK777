# pages/Calculator.py

import streamlit as st  # type: ignore
import pandas as pd

@st.cache_data(ttl=900)
def load_calc_data() -> dict[str, pd.DataFrame]:
    """
    Load all sheets from calc_data_250706.xlsx.
    """
    file_path = "data/calc_data_250706.xlsx"
    sheet_map = {
        "hq":                 "hq_requirements",
        "bdg":                "bdg",
        "gear":               "gear",
        "drone":              "drone",
        "hero_exp":           "hero_exp",
        "hero_skill":         "hero_skill",
        "hero_weapon":        "hero_weapon",
        "overlord_training":  "overlord_training",
        "overlord_exp":       "overlord_exp",
        "overlord_skill":     "overlord_skill",
        "overlord_bond":      "overlord_bond",
    }
    data: dict[str, pd.DataFrame] = {}
    for key, sheet in sheet_map.items():
        try:
            if key == "bdg":
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet,
                    converters={"time_hms": str}
                )
            else:
                df = pd.read_excel(file_path, sheet_name=sheet)
            data[key] = df
        except Exception as e:
            st.error(f"❌ '{sheet}' 시트 로드 실패: {e}")
            data[key] = pd.DataFrame()
    return data

def format_resource(val):
    try:
        x = float(val)
    except Exception:
        return str(val)
    if abs(x) >= 1e9:
        return f"{x/1e9:.3f} G"
    elif abs(x) >= 1e6:
        return f"{x/1e6:.1f} M"
    elif abs(x) >= 1e3:
        return f"{x/1e3:.1f} k"
    else:
        return f"{int(x):,}"

def render(_load_sheet):
    st.title("📊 참고자료/계산기")
    data = load_calc_data()

    categories: dict[str, tuple[str, str, list[str]]] = {
        "🏰 본부 업그레이드 조건": ("hq",   "hq_lvl",                    []),
        "🏗️ 건물 자원/시간":       ("bdg",  "bdg_lvl",                  []),
        "⚙️ 장비 제작":            ("gear", "Gear_names",              ["coins","ores","ceramics","yellow_blueprint","red_blueprint"]),
        "🚁 드론 업그레이드":       ("drone", "drone_level",             ["drone_parts"]),
        "영웅 경험치":            ("hero_exp",          "hero_lvl",            ["hero_exp"]),
        "영웅 스킬훈장":          ("hero_skill",        "hero_skill_lvl",      ["hero_skill_medal"]),
        "영웅 전속무기":          ("hero_weapon",       "hero_weapon_lvl",     ["hero_weapon_shard"]),
        "오버로드 특수훈련":       ("overlord_training","overlord_training_lvl",["guidebook","certificates"]),
        "오버로드 레벨/조각":     ("overlord_exp",      "overlord_lvl",        ["overlord_shard"]),
        "오버로드 스킬 메달":     ("overlord_skill",     "overlord_skill_lvl",  ["overlord_skill_medal"]),
        "오버로드 친밀도 뱃지":   ("overlord_bond",     "overlord_bond_name",  ["overlord_bond_badge"]),
    }

    choice = st.selectbox("카테고리 선택", list(categories.keys()))
    key, lvl_col, val_cols = categories[choice]
    df = data.get(key, pd.DataFrame())

    if df.empty:
        st.warning(f"{choice} 데이터가 없습니다.")
        return

    # 1. HQ upgrade requirements
    if choice == "🏰 본부 업그레이드 조건":
        st.subheader("🏰 본부 업그레이드 조건 전체 데이터")
        st.dataframe(df, use_container_width=True)
        return

    # 2. BDG (building resources/time)
    if choice == "🏗️ 건물 자원/시간":
        col1, col2 = st.columns(2)
        with col1:
            bld = st.selectbox("건물 종류", sorted(df["Buildings"].unique()))
            lvls = sorted(df[df["Buildings"] == bld]["bdg_lvl"].astype(int))
            lvl = st.selectbox("건물 레벨", lvls)
        with col2:
            rss_buff = st.slider("자원감소(%)", min_value=0.0, max_value=30.0, value=0.0, step=0.1)
            time_buff = st.slider("건설가속(%)", min_value=100, max_value=400, value=100, step=1)

        row = df[(df["Buildings"] == bld) & (df["bdg_lvl"] == lvl)].squeeze()
        days = int(row["time_day"])
        hms = row["time_hms"]

        def parse_time(days, hms):
            try:
                h, m, s = map(int, hms.split(':'))
            except Exception:
                h, m, s = 0, 0, 0
            total_minutes = days * 24 * 60 + h * 60 + m + s / 60
            return int(total_minutes)

        def format_time(total_minutes):
            days = total_minutes // (24 * 60)
            rem = total_minutes % (24 * 60)
            hours = rem // 60
            minutes = rem % 60
            return f"{days}일 {hours}시간 {minutes}분"

        min0 = parse_time(days, hms)
        min1 = min0 / (time_buff * 0.01)
        iron_buff = row['Iron'] * (1 - rss_buff * 0.01)
        food_buff = row['Food'] * (1 - rss_buff * 0.01)
        coins_buff = row['Coins'] * (1 - rss_buff * 0.01)

        col3, col4 = st.columns(2)
        with col3:
            st.write("버프 미적용")
            st.metric("철",   format_resource(row['Iron']))
            st.metric("식량", format_resource(row['Food']))
            st.metric("금화", format_resource(row['Coins']))
            st.metric("소요 시간", format_time(min0))
        with col4:
            st.write("버프 적용 후")
            st.metric("철",   format_resource(iron_buff))
            st.metric("식량", format_resource(food_buff))
            st.metric("금화", format_resource(coins_buff))
            st.metric("소요 시간", format_time(int(min1)))
        return

    # 3. Gear upgrade or other level-sum categories
    options = df[lvl_col].tolist()
    curr = st.selectbox("현재", options, index=0, key=f"{key}_curr")
    tgt  = st.selectbox("목표", options, index=1, key=f"{key}_tgt")

    # Determine masks
    if df[lvl_col].dtype == object:
        i_curr = options.index(curr)
        i_tgt  = options.index(tgt)
        if i_tgt < i_curr:
            st.error("목표 값이 현재 값보다 낮습니다.")
            return
        mask_curr   = df.index <= i_curr
        mask_tgt    = df.index <= i_tgt
        mask_between= df.index.isin(range(i_curr+1, i_tgt+1))
    else:
        c, t = int(curr), int(tgt)
        if t < c:
            st.error("목표 레벨이 현재 레벨보다 낮습니다.")
            return
        mask_curr   = df[lvl_col].astype(int) <= c
        mask_tgt    = df[lvl_col].astype(int) <= t
        mask_between= (df[lvl_col].astype(int) > c) & (df[lvl_col].astype(int) <= t)

    # Check data readiness
    if mask_between.sum() == 0 or df.loc[mask_between, val_cols].astype(str).isin(["-1",""]).any().any():
        st.error("해당 구간의 데이터가 준비되지 않았습니다")
        return

    # Sum calculation: sum(0~tgt) - sum(0~curr)
    for col in val_cols:
        sum_tgt  = df.loc[mask_tgt,   col].astype(float).sum()
        sum_curr = df.loc[mask_curr,  col].astype(float).sum()
        need     = sum_tgt - sum_curr
        st.metric(col.replace("_"," ").title(), format_resource(need))
