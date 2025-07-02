# utils/data_loader.py
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
import os

BACKUP_EXCEL_PATH = "data/250628_1800.xlsx"

@st.cache_resource
def _init_gs_client():
    """Google Sheets 클라이언트 초기화 (캐시됨)"""
    try:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["connections"]["gsheets"]
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Sheets 클라이언트 초기화 실패: {e}")
        return None

def _load_from_gsheets(sheet_name: str):
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
        st.success("✅ Google Sheets에서 데이터 로드 성공")
        return df
    except Exception as e:
        st.warning(f"Google Sheets 로드 실패: {e}")
        return None

def _load_from_excel(path: str, sheet_name: str):
    """Excel 백업 파일에서 데이터 로드"""
    try:
        if not os.path.exists(path):
            st.error(f"Excel 백업 파일을 찾을 수 없습니다: {path}")
            return None
            
        df = pd.read_excel(path, sheet_name=sheet_name)
        st.info("📁 Excel 백업에서 데이터 로드 성공")
        return df
    except Exception as e:
        st.error(f"Excel 백업 로드 실패: {e}")
        return None

def load_dataframe_with_fallback(sheet_name: str, excel_sheet: str = None):
    """
    Google Sheets 우선 로드, 실패 시 로컬 Excel로 폴백
    """
    # 먼저 Google Sheets에서 시도
    df = _load_from_gsheets(sheet_name)
    
    # Google Sheets 실패 시 Excel 백업 사용
    if df is None:
        excel_path = BACKUP_EXCEL_PATH
        if not os.path.isabs(excel_path):
            # 상대 경로인 경우 현재 작업 디렉토리 기준으로 처리
            excel_path = os.path.join(os.getcwd(), excel_path)
        df = _load_from_excel(excel_path, sheet_name=excel_sheet or sheet_name)
    
    return df if df is not None else pd.DataFrame()

def get_excel_sheet_names(path: str = BACKUP_EXCEL_PATH):
    """백업 Excel 파일 내 시트 목록 조회"""
    try:
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
            
        if not os.path.exists(path):
            st.error(f"Excel 파일을 찾을 수 없습니다: {path}")
            return []
            
        xl = pd.ExcelFile(path)
        return xl.sheet_names
    except Exception as e:
        st.error(f"Excel 시트 조회 실패: {e}")
        return []

# 데이터 저장 함수 추가 (Google Sheets에 쓰기)
def save_dataframe_to_gsheets(df: pd.DataFrame, sheet_name: str):
    """데이터프레임을 Google Sheets에 저장"""
    try:
        client = _init_gs_client()
        if client is None:
            st.error("Google Sheets 클라이언트 초기화 실패로 저장할 수 없습니다.")
            return False
            
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sh = client.open_by_url(url)
        
        try:
            ws = sh.worksheet(sheet_name)
            # 기존 시트 내용 지우기
            ws.clear()
        except gspread.WorksheetNotFound:
            # 시트가 없으면 새로 생성
            ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=20)
        
        # 데이터프레임을 리스트로 변환하여 업데이트
        # 헤더 포함
        data = [df.columns.values.tolist()] + df.values.tolist()
        ws.update(data)
        
        st.success(f"✅ Google Sheets '{sheet_name}' 시트에 데이터 저장 성공")
        return True
        
    except Exception as e:
        st.error(f"Google Sheets 저장 실패: {e}")
        return False

# 백업용 Excel 저장 함수
def save_dataframe_to_excel(df: pd.DataFrame, path: str = BACKUP_EXCEL_PATH, sheet_name: str = "Sheet1"):
    """데이터프레임을 Excel 파일에 저장"""
    try:
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
            
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # 기존 파일이 있으면 기존 시트들과 함께 저장
        if os.path.exists(path):
            with pd.ExcelWriter(path, mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # 새 파일 생성
            df.to_excel(path, sheet_name=sheet_name, index=False)
            
        st.info(f"📁 Excel 파일 '{path}'에 '{sheet_name}' 시트 저장 성공")
        return True
        
    except Exception as e:
        st.error(f"Excel 파일 저장 실패: {e}")
        return False
