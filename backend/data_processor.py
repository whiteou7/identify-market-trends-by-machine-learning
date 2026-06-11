import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

_BASE = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(_BASE, "..", "dataset", "coin_Bitcoin.csv")


def _engineer_features(df: pd.DataFrame, window: int):
    """
    Shared Phase-1 pipeline. Expects df to have 'Date' (datetime) and 'Close' columns.
    Returns (df_with_features, X_scaled, feature_cols, scaler).
    """
    df = df[df["Close"].notna()].copy()

    # Log Return: ln(Close_t / Close_{t-1})
    df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))

    # Volatility: rolling std of log returns
    df["volatility"] = df["log_return"].rolling(window=window).std()
    df["volatility_14"] = df["log_return"].rolling(window=14).std()

    # Momentum: rate of change over window days
    df["momentum"] = (df["Close"] - df["Close"].shift(window)) / df["Close"].shift(window)
    df["momentum_30"] = (df["Close"] - df["Close"].shift(30)) / df["Close"].shift(30)

    df = df.dropna().reset_index(drop=True)

    feature_cols = ["log_return", "volatility", "momentum"]
    X = df[feature_cols].values

    # Scaling — mandatory before K-Means (Euclidean distance)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return df, X_scaled, feature_cols, scaler


def load_and_process(window: int = 7):
    """Load default coin_Bitcoin.csv and run feature engineering."""
    df = pd.read_csv(DATASET_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return _engineer_features(df, window)


def process_uploaded(raw_df: pd.DataFrame, detection: dict, window: int = 7):
    """
    Normalise an uploaded DataFrame using the detected column mapping,
    then run the same feature engineering pipeline.

    Handles:
      - Unix timestamps (seconds or milliseconds)
      - Sub-daily data (resampled to daily OHLCV via last close)
    """
    date_col = detection["date_col"]
    close_col = detection["close_col"]

    df = raw_df[[date_col, close_col]].copy()
    df.columns = ["Date", "Close"]
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    # Parse dates
    if detection.get("is_unix_timestamp"):
        unit = "ms" if detection.get("is_unix_ms") else "s"
        df["Date"] = pd.to_datetime(df["Date"], unit=unit, utc=True).dt.tz_localize(None)
    else:
        df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date").reset_index(drop=True)
    df = df.dropna(subset=["Close"])

    # Resample sub-daily data to daily (e.g., 1-minute BTC data)
    if len(df) > 1:
        median_diff = df["Date"].diff().dropna().median()
        if median_diff < pd.Timedelta("20 hours"):
            df = (
                df.set_index("Date")["Close"]
                .resample("D")
                .last()
                .dropna()
                .reset_index()
            )
            df.columns = ["Date", "Close"]

    return _engineer_features(df, window)
