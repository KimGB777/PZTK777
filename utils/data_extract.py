# utils/data_extract.py

import pandas as pd
from typing import List, Dict

def sort_content(items: List[str]) -> List[str]:
    """
    Split each string by line, strip whitespace, remove empties,
    dedupe and return sorted list of lines.
    """
    lines = []
    for text in items:
        if isinstance(text, str):
            for ln in text.split("\n"):
                ln = ln.strip()
                if ln:
                    lines.append(ln)
    return sorted(set(lines))

def extract_section(
    df_map: Dict[str, pd.DataFrame],
    cols: List[str]
) -> List[str]:
    """
    Generic extractor: for each column in `cols`, looks up df_map[col],
    takes its first row value if present & non-null, collects into a list,
    then sorts via sort_content.
    
    df_map: { column_name: DataFrame }
    cols:   list of column names to extract
    """
    contents = []
    for col in cols:
        df = df_map.get(col)
        if df is None or df.empty or col not in df.columns:
            continue
        val = df.iloc[0][col]
        if pd.notna(val):
            contents.append(str(val))
    return sort_content(contents)

def format_content_display(lines: List[str], icon: str = "•") -> List[str]:
    """
    각 줄 앞에 아이콘을 붙인 마크다운 표시용 리스트를 생성합니다.
    """
    return [f"{icon} {ln}" for ln in lines if ln.strip()]