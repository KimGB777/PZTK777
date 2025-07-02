# utils/data_loader.py
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
import os
from typing import Optional

BACKUP_EXCEL_PATH = "data/250628_1800.xlsx"

# Google Sheets 클라이언트 (캐시됨)
@st.cache_resource
def _init_gs_client() -> Optional[gspread.Client]:
    """Google Sheets 클라이언트 초기화 (올바른 스코프 포함)"""
    try:
        gsheets_config = st.secrets["connections"]["gsheets"]
        scopes = gsheets_config.get("scopes", [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        
        creds = service_account.Credentials.from_service_account_info(
            gsheets_config,
            scopes=scopes
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.warning(f"Google Sheets 클라이언트 초기화 실패: {e}")
        return None

def _load_from_gsheets(sheet_name: str) -> Optional[pd.DataFrame]:
    """Google Sheets에서 데이터 로드"""
    try:
        client = _init_gs_client()
        if client is None:
            return None
            
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        ws = sh.worksheet(sheet_name)
        records = ws.get_all_records()
        df = pd.DataFrame(records)
        
        if not df.empty:
            st.success(f"✅ Google Sheets에서 '{sheet_name}' 로드 성공")
        return df
    except Exception as e:
        st.warning(f"Google Sheets '{sheet_name}' 로드 실패: {e}")
        return None

def _load_from_excel(path: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """Excel 백업 파일에서 데이터 로드"""
    try:
        if not os.path.exists(path):
            st.error(f"Excel 백업 파일을 찾을 수 없습니다: {path}")
            return None
            
        df = pd.read_excel(path, sheet_name=sheet_name)
        st.info(f"📁 Excel 백업에서 '{sheet_name}' 로드 성공")
        return df
    except Exception as e:
        st.error(f"Excel '{sheet_name}' 로드 실패: {e}")
        return None

def load_dataframe_with_fallback(sheet_name: str, excel_sheet: str = None) -> pd.DataFrame:
    """Google Sheets 우선 로드, 실패 시 Excel 폴백"""
    # Google Sheets 시도
    df = _load_from_gsheets(sheet_name)
    
    # 실패 시 Excel 백업 사용
    if df is None or df.empty:
        excel_path = BACKUP_EXCEL_PATH
        if not os.path.isabs(excel_path):
            excel_path = os.path.join(os.getcwd(), excel_path)
        df = _load_from_excel(excel_path, sheet_name=excel_sheet or sheet_name)
    
    return df if df is not None else pd.DataFrame()

def save_dataframe_to_gsheets(df: pd.DataFrame, sheet_name: str) -> bool:
    """데이터프레임을 Google Sheets에 저장"""
    try:
        client = _init_gs_client()
        if client is None:
            st.error("Google Sheets 클라이언트 초기화 실패")
            return False
            
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        
        try:
            ws = sh.worksheet(sheet_name)
            ws.clear()
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=20)
        
        # 헤더 포함하여 업데이트
        data = [df.columns.tolist()] + df.values.tolist()
        ws.update(data)
        
        st.success(f"✅ Google Sheets '{sheet_name}' 저장 성공")
        return True
    except Exception as e:
        st.error(f"Google Sheets 저장 실패: {e}")
        return False

def get_excel_sheet_names(path: str = BACKUP_EXCEL_PATH) -> list:
    """Excel 파일의 시트 목록 조회"""
    try:
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            return []
        xl = pd.ExcelFile(path)
        return xl.sheet_names
    except Exception:
        return []
