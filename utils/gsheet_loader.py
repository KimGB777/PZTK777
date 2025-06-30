# utils/gsheet_loader.py
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Worksheet name mapping
SHEETS = {
    "daily": "daily",
    "weekly": "weekly", 
    "monthly": "monthly",
    "note": "note"
}

@st.cache_data(ttl=900)  # 15분 캐시 (300초 -> 900초로 증가)
def load_gsheet_data() -> Dict[str, pd.DataFrame]:
    try:
        # 연결 설정 확인
        if not hasattr(st, 'secrets') or 'gsheets' not in st.secrets:
            logger.error("Google Sheets 설정이 없습니다.")
            raise Exception("Google Sheets 연결 설정이 누락되었습니다. secrets.toml을 확인해주세요.")
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        dfs = {}
        
        for key, ws_name in SHEETS.items():
            try:
                logger.info(f"Loading worksheet: {ws_name}")
                
                # 워크시트 데이터 읽기
                df = conn.read(
                    worksheet=ws_name,
                    usecols=lambda _: True,
                    nrows=None  # 모든 행 읽기
                )
                
                # 데이터 검증 및 전처리
                if df is not None and not df.empty:
                    # 날짜 컬럼 처리 (일일데이터의 경우)
                    if key == "daily" and "Date" in df.columns:
                        try:
                            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                            # 잘못된 날짜 제거
                            df = df.dropna(subset=['Date'])
                            logger.info(f"Processed {len(df)} rows with valid dates")
                        except Exception as e:
                            logger.warning(f"Date conversion error for {ws_name}: {e}")
                    
                    # 빈 행 제거
                    df = df.dropna(how='all')
                    
                    # 컬럼명 정리 (앞뒤 공백 제거)
                    df.columns = df.columns.str.strip()
                    
                    dfs[key] = df
                    logger.info(f"Successfully loaded {ws_name}: {len(df)} rows, {len(df.columns)} columns")
                else:
                    logger.warning(f"Empty worksheet: {ws_name}")
                    dfs[key] = pd.DataFrame()
                    
            except Exception as e:
                logger.error(f"Failed to load worksheet {ws_name}: {e}")
                # 실패한 워크시트는 빈 DataFrame으로 처리
                dfs[key] = pd.DataFrame()
        
        # 최소한 하나의 워크시트라도 로드되었는지 확인
        loaded_sheets = [k for k, v in dfs.items() if not v.empty]
        if not loaded_sheets:
            logger.error("모든 워크시트 로드 실패")
            raise Exception("Google Sheets 데이터를 불러올 수 없습니다.")
        
        logger.info(f"Successfully loaded {len(loaded_sheets)} worksheets: {loaded_sheets}")
        return dfs
        
    except Exception as e:
        logger.error(f"Google Sheets 데이터 로드 실패: {e}")
        raise

def clear_cache():
    """캐시 데이터를 강제로 삭제합니다."""
    load_gsheet_data.clear()
    logger.info("Google Sheets 캐시가 초기화되었습니다.")

def get_sheet_info() -> Dict[str, str]:
    return SHEETS.copy()