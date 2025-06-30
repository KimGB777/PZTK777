# utils/data_extract.py
import pandas as pd
from typing import Dict, List, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sort_content(items: List[str]) -> List[str]:
    """
    문자열 목록을 정렬하고 중복을 제거합니다.
    
    Args:
        items: 정렬할 문자열 목록
        
    Returns:
        List[str]: 정렬되고 중복이 제거된 문자열 목록
    """
    lines: List[str] = []
    
    for text in items:
        if isinstance(text, str) and text.strip():
            # 줄바꿈으로 분할하고 빈 줄 제거
            split_lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
            lines.extend(split_lines)
    
    # 중복 제거하되 순서는 유지
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    
    return sorted(unique_lines)

def extract_section(
    df_map: Dict[str, pd.DataFrame],
    cols: List[str]
) -> List[str]:
    """
    데이터프레임 맵에서 지정된 컬럼들의 데이터를 추출합니다.
    
    Args:
        df_map: 데이터프레임 딕셔너리
        cols: 추출할 컬럼명 목록
        
    Returns:
        List[str]: 추출된 데이터 목록
    """
    raw: List[str] = []
    
    try:
        for col in cols:
            df = df_map.get(col)
            
            if df is not None and not df.empty:
                if col in df.columns:
                    # 첫 번째 행의 해당 컬럼 값 추출
                    val = df.iloc[0][col]
                    
                    if pd.notna(val) and str(val).strip():
                        raw.append(str(val).strip())
                        logger.debug(f"Extracted from {col}: {str(val)[:50]}...")
                else:
                    logger.warning(f"Column '{col}' not found in dataframe")
            else:
                logger.debug(f"Empty or missing dataframe for column '{col}'")
        
        return sort_content(raw)
        
    except Exception as e:
        logger.error(f"Error extracting section: {e}")
        return []

def format_content_display(lines: List[str], icon: str) -> List[str]:
    """
    컨텐츠 목록에 아이콘을 추가하여 표시 형식을 만듭니다.
    
    Args:
        lines: 표시할 텍스트 목록
        icon: 추가할 아이콘
        
    Returns:
        List[str]: 포맷된 텍스트 목록
    """
    return [f"{icon} {ln}" for ln in lines if ln and ln.strip()]

def extract_multiple_sections(
    df_map: Dict[str, pd.DataFrame],
    section_configs: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    여러 섹션을 한 번에 추출합니다.
    
    Args:
        df_map: 데이터프레임 딕셔너리
        section_configs: 섹션별 컬럼 설정
        
    Returns:
        Dict[str, List[str]]: 섹션별 추출된 데이터
    """
    results = {}
    
    for section_name, columns in section_configs.items():
        try:
            results[section_name] = extract_section(df_map, columns)
            logger.debug(f"Extracted {len(results[section_name])} items for {section_name}")
        except Exception as e:
            logger.error(f"Error extracting {section_name}: {e}")
            results[section_name] = []
    
    return results

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    데이터프레임이 필요한 컬럼을 포함하고 있는지 검증합니다.
    
    Args:
        df: 검증할 데이터프레임
        required_columns: 필요한 컬럼 목록
        
    Returns:
        bool: 검증 통과 여부
    """
    if df is None or df.empty:
        return False
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logger.warning(f"Missing required columns: {missing_columns}")
        return False
    
    return True