# utils/data_extract.py
import pandas as pd
from typing import List, Dict, Union

def sort_content(items: List[str]) -> List[str]:
    """문자열 리스트를 줄 단위로 분리, 정리, 정렬"""
    lines = []
    for text in items:
        if not isinstance(text, str):
            continue
        for ln in text.splitlines():
            ln = ln.strip()
            if ln:
                lines.append(ln)
    return sorted(set(lines))

def extract_section(
    df_map: Dict[str, Union[pd.DataFrame, pd.Series]],
    cols: List[str]
) -> List[str]:
    """
    DataFrame/Series 맵에서 지정된 컬럼들의 데이터를 추출하여 정리된 리스트 반환
    """
    contents: List[str] = []
    
    for col in cols:
        data = df_map.get(col)
        if data is None:
            continue
            
        # DataFrame 처리
        if isinstance(data, pd.DataFrame):
            if col not in data.columns or data.empty:
                continue
            cell = data.iloc[0, data.columns.get_indexer([col])[0]]
        # Series 처리
        elif isinstance(data, pd.Series):
            if data.empty:
                continue
            cell = data.iloc[0]
        else:
            continue
            
        # null 체크 후 문자열 변환
        if pd.notna(cell):
            contents.append(str(cell))
    
    return sort_content(contents)

def format_content_display(lines: List[str], icon: str = "•") -> List[str]:
    """각 줄 앞에 아이콘을 붙여 Markdown 표시용 리스트 생성"""
    return [f"{icon} {ln}" for ln in lines if ln.strip()]
