"""
Tự động phát hiện cột ngày và cột close/giá từ CSV được tải lên.

Hỗ trợ các định dạng phổ biến:
  - Yahoo Finance: Date, Close / Adj Close
  - Binance: Open time (Unix ms), Close
  - Kaggle BTC 1-min: Timestamp (Unix s), Close
  - CoinGecko: snapped_at, price
  - coin_Bitcoin.csv: Date, Close
"""
import numpy as np
import pandas as pd

# Sắp xếp theo độ ưu tiên (chữ thường): tên cụ thể hơn hoặc phổ biến hơn đứng trước
# để CSV không rõ ràng (ví dụ: có cả "time" và "timestamp") được xử lý nhất quán.
_DATE_KEYWORDS = ['timestamp', 'date', 'time', 'datetime', 'open time', 'close time',
                  'snapped_at', 'period', 'dt']
_CLOSE_KEYWORDS = ['adj close', 'adjclose', 'adj_close', 'close', 'price', 'last',
                   'settle', 'settlement']
# Các cột trông có vẻ số nhưng chắc chắn không phải chuỗi giá.
_EXCLUDE_FROM_CLOSE = {
    'volume', 'vol', 'amount', 'marketcap', 'market cap', 'market_cap',
    'sno', 'no', 'number', 'high', 'low', 'open', 'open time', 'close time',
    'quote asset volume', 'taker buy base', 'taker buy quote', 'ignore',
}


def detect_columns(df: pd.DataFrame) -> dict:
    """
    Trả về:
        date_col: str | None
        close_col: str | None
        is_unix_timestamp: bool  — True khi cột ngày chứa số nguyên Unix epoch
        is_unix_ms: bool         — True khi Unix epoch tính bằng mili-giây (> 1e12)
    """
    cols = df.columns.tolist()
    lower_map: dict[str, str] = {c.lower().strip(): c for c in cols}

    # --- cột ngày ---
    date_col = _find_by_keywords(_DATE_KEYWORDS, lower_map)
    if date_col is None:
        # Fallback mở rộng hơn: bất kỳ cột nào có tên chứa date/time/stamp
        for orig in cols:
            low = orig.lower()
            if any(tok in low for tok in ('date', 'time', 'stamp')):
                date_col = orig
                break

    # --- cột close/giá ---
    close_col = _find_by_keywords(_CLOSE_KEYWORDS, lower_map)
    if close_col is None:
        # Fallback: các cột số không nằm trong danh sách loại trừ
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        candidates = [c for c in num_cols if c.lower().strip() not in _EXCLUDE_FROM_CLOSE]
        # Ưu tiên cột có tên chứa 'close' hoặc 'price'
        for c in candidates:
            low = c.lower()
            if 'close' in low or 'price' in low:
                close_col = c
                break
        if close_col is None and candidates:
            # Trong bố cục OHLCV chuẩn, cột Close nằm sau High/Low/Open,
            # nên lấy cột số cuối cùng là heuristic hợp lý khi không còn lựa chọn nào khác.
            close_col = candidates[-1]

    # --- Phát hiện Unix timestamp ---
    is_unix_ts = False
    is_unix_ms = False
    if date_col is not None and pd.api.types.is_numeric_dtype(df[date_col]):
        is_unix_ts = True
        sample = df[date_col].dropna().iloc[0] if len(df) > 0 else 0
        # Unix epoch giây tối đa khoảng 2.5e9 cho các ngày trong thế kỷ này;
        # epoch mili-giây lớn hơn ba bậc độ lớn (> 1e12).
        is_unix_ms = float(sample) > 1e12

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
