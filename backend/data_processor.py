import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

_BASE = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(_BASE, "..", "dataset", "coin_Bitcoin.csv")


def _engineer_features(df: pd.DataFrame, window: int):
    """
    Pipeline chung Giai đoạn 1. Đầu vào df cần có cột 'Date' (datetime) và 'Close'.
    Trả về (df_có_đặc_trưng, X_scaled, feature_cols, scaler).
    """
    df = df[df["Close"].notna()].copy()

    # Log Return: ln(Close_t / Close_{t-1})
    df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))

    # Volatility: độ lệch chuẩn rolling của log return
    df["volatility"] = df["log_return"].rolling(window=window).std()
    df["volatility_14"] = df["log_return"].rolling(window=14).std()

    # Momentum: tỉ lệ thay đổi giá trong window ngày
    df["momentum"] = (df["Close"] - df["Close"].shift(window)) / df["Close"].shift(window)
    df["momentum_30"] = (df["Close"] - df["Close"].shift(30)) / df["Close"].shift(30)

    df = df.dropna().reset_index(drop=True)

    # Chỉ biến thể cửa sổ ngắn mới đưa vào mô hình; cột 14 ngày / 30 ngày
    # được giữ lại trong df để phân tích tiếp theo nhưng loại khỏi X.
    feature_cols = ["log_return", "volatility", "momentum"]
    X = df[feature_cols].values

    # Chuẩn hoá là bắt buộc trước K-Means: khoảng cách Euclidean bị chi phối
    # bởi đặc trưng có thang giá trị lớn nhất (return << volatility << momentum).
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return df, X_scaled, feature_cols, scaler


def load_and_process(window: int = 7):
    """Tải coin_Bitcoin.csv mặc định và chạy pipeline tạo đặc trưng."""
    df = pd.read_csv(DATASET_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return _engineer_features(df, window)


def process_uploaded(raw_df: pd.DataFrame, detection: dict, window: int = 7):
    """
    Chuẩn hoá DataFrame đã tải lên theo ánh xạ cột được phát hiện,
    sau đó chạy cùng pipeline tạo đặc trưng.

    Xử lý:
      - Unix timestamp (giây hoặc mili-giây)
      - Dữ liệu dưới mức ngày (resample về OHLCV ngày theo giá close cuối cùng)
    """
    date_col = detection["date_col"]
    close_col = detection["close_col"]

    df = raw_df[[date_col, close_col]].copy()
    df.columns = ["Date", "Close"]
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    # Phân tích ngày tháng
    if detection.get("is_unix_timestamp"):
        unit = "ms" if detection.get("is_unix_ms") else "s"
        df["Date"] = pd.to_datetime(df["Date"], unit=unit, utc=True).dt.tz_localize(None)
    else:
        df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date").reset_index(drop=True)
    df = df.dropna(subset=["Close"])

    # Resample dữ liệu dưới mức ngày về ngày (ví dụ: dữ liệu BTC 1 phút)
    if len(df) > 1:
        median_diff = df["Date"].diff().dropna().median()
        # Ngưỡng 20 giờ phân biệt dữ liệu intraday thật sự với dữ liệu ngày
        # có khoảng cách 25 giờ do cuối tuần hoặc phiên giao dịch bị thiếu.
        if median_diff < pd.Timedelta("20 hours"):
            # Lấy giá close cuối cùng của mỗi ngày dương lịch, khớp với cách trích dẫn OHLCV ngày.
            df = (
                df.set_index("Date")["Close"]
                .resample("D")
                .last()
                .dropna()
                .reset_index()
            )
            df.columns = ["Date", "Close"]

    return _engineer_features(df, window)
