# utils/data_extract.py
import pandas as pd
from typing import Dict, List

def sort_content(items: List[str]) -> List[str]:
    lines: List[str] = []
    for text in items:
        if isinstance(text, str):
            lines += [ln.strip() for ln in text.split("\n") if ln.strip()]
    return sorted(set(lines))

def extract_section(
    df_map: Dict[str, pd.DataFrame],
    cols: List[str]
) -> List[str]:
    raw: List[str] = []
    for col in cols:
        df = df_map.get(col)
        if df is not None and not df.empty and col in df.columns:
            val = df.iloc[0][col]
            if pd.notna(val):
                raw.append(str(val))
    return sort_content(raw)

def format_content_display(lines: List[str], icon: str) -> List[str]:
    return [f"{icon} {ln}" for ln in lines]
