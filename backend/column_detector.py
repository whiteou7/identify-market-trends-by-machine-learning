"""
Auto-detect date and close/price columns from an uploaded CSV.

Supports common formats:
  - Yahoo Finance: Date, Close / Adj Close
  - Binance: Open time (Unix ms), Close
  - Kaggle BTC 1-min: Timestamp (Unix s), Close
  - CoinGecko: snapped_at, price
  - coin_Bitcoin.csv: Date, Close
"""
import numpy as np
import pandas as pd

# Ordered by preference (lowercase)
_DATE_KEYWORDS = ['timestamp', 'date', 'time', 'datetime', 'open time', 'close time',
                  'snapped_at', 'period', 'dt']
_CLOSE_KEYWORDS = ['adj close', 'adjclose', 'adj_close', 'close', 'price', 'last',
                   'settle', 'settlement']
_EXCLUDE_FROM_CLOSE = {
    'volume', 'vol', 'amount', 'marketcap', 'market cap', 'market_cap',
    'sno', 'no', 'number', 'high', 'low', 'open', 'open time', 'close time',
    'quote asset volume', 'taker buy base', 'taker buy quote', 'ignore',
}


def detect_columns(df: pd.DataFrame) -> dict:
    """
    Returns:
        date_col: str | None
        close_col: str | None
        is_unix_timestamp: bool  — True when date column contains Unix epoch integers
        is_unix_ms: bool         — True when Unix epoch is in milliseconds (> 1e12)
    """
    cols = df.columns.tolist()
    lower_map: dict[str, str] = {c.lower().strip(): c for c in cols}

    # --- date column ---
    date_col = _find_by_keywords(_DATE_KEYWORDS, lower_map)
    if date_col is None:
        # Broader fallback: any column whose name contains date/time/stamp
        for orig in cols:
            low = orig.lower()
            if any(tok in low for tok in ('date', 'time', 'stamp')):
                date_col = orig
                break

    # --- close/price column ---
    close_col = _find_by_keywords(_CLOSE_KEYWORDS, lower_map)
    if close_col is None:
        # Fallback: numeric columns not in the exclusion list
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        candidates = [c for c in num_cols if c.lower().strip() not in _EXCLUDE_FROM_CLOSE]
        # Prefer any column whose name contains 'close' or 'price'
        for c in candidates:
            low = c.lower()
            if 'close' in low or 'price' in low:
                close_col = c
                break
        if close_col is None and candidates:
            # Last remaining numeric column (Close is typically rightmost in OHLCV)
            close_col = candidates[-1]

    # --- Unix timestamp detection ---
    is_unix_ts = False
    is_unix_ms = False
    if date_col is not None and pd.api.types.is_numeric_dtype(df[date_col]):
        is_unix_ts = True
        sample = df[date_col].dropna().iloc[0] if len(df) > 0 else 0
        is_unix_ms = float(sample) > 1e12   # ms epoch > 1 trillion

    return {
        'date_col': date_col,
        'close_col': close_col,
        'is_unix_timestamp': is_unix_ts,
        'is_unix_ms': is_unix_ms,
    }


def _find_by_keywords(keywords: list[str], lower_map: dict[str, str]) -> str | None:
    for kw in keywords:
        if kw in lower_map:
            return lower_map[kw]
    return None
