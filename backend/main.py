import io
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from clustering import find_optimal_k, run_gmm, run_kmeans
from column_detector import detect_columns
from data_processor import load_and_process, process_uploaded

app = FastAPI(title="Market Trend Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lưu trữ trong bộ nhớ cho dataset đã tải lên (ứng dụng đơn người dùng / demo)
# ---------------------------------------------------------------------------
_upload: dict = {
    "raw_df": None,
    "detection": None,
    "filename": None,
    "daily_rows": 0,
    "date_range": None,
}


def _get_data(use_uploaded: bool, window: int):
    """Trả về (df, X_scaled, feature_cols, scaler), chuyển hướng đến dataset đã tải lên
    khi có dataset và use_uploaded là True, ngược lại dùng CSV mặc định."""
    if use_uploaded and _upload["raw_df"] is not None:
        return process_uploaded(_upload["raw_df"], _upload["detection"], window)
    return load_and_process(window)


# ---------------------------------------------------------------------------
# Kiểm tra trạng thái
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Tải lên dataset
# ---------------------------------------------------------------------------

@app.get("/api/upload/info")
def get_upload_info():
    """Trả về trạng thái tải lên hiện tại (frontend gọi khi tải trang)."""
    if _upload["raw_df"] is None:
        return {"has_upload": False}
    return {
        "has_upload": True,
        "filename": _upload["filename"],
        "daily_rows": _upload["daily_rows"],
        "date_range": _upload["date_range"],
        "detected": {
            "date_col": _upload["detection"]["date_col"],
            "close_col": _upload["detection"]["close_col"],
            "is_unix_timestamp": _upload["detection"]["is_unix_timestamp"],
        },
    }


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported.")

    content = await file.read()
    # Giới hạn 500 MB để kiểm soát bộ nhớ; CSV BTC 1 phút toàn bộ lịch sử khoảng ~300 MB.
    if len(content) > 500 * 1024 * 1024:
        raise HTTPException(413, "File too large. Maximum size is 500 MB.")

    try:
        raw_df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(422, f"Could not parse CSV: {e}")

    if len(raw_df) == 0:
        raise HTTPException(422, "CSV file is empty.")

    detection = detect_columns(raw_df)
    # Giới hạn xem trước 12 cột để thông báo lỗi dễ đọc trên giao diện.
    col_list = ", ".join(raw_df.columns[:12].tolist())

    if detection["date_col"] is None:
        raise HTTPException(
            422,
            f"No date/time column found. Detected columns: {col_list}. "
            "Expected a column named 'Date', 'Timestamp', 'Open time', etc.",
        )
    if detection["close_col"] is None:
        raise HTTPException(
            422,
            f"No price/close column found. Detected columns: {col_list}. "
            "Expected a column named 'Close', 'Price', 'Adj Close', etc.",
        )

    try:
        df, _, _, _ = process_uploaded(raw_df, detection, window=7)
    except Exception as e:
        raise HTTPException(422, f"Failed to process dataset: {e}")

    # 30 hàng ngày là tối thiểu để cửa sổ rolling volatility có ý nghĩa và
    # đủ phương sai để tính điểm silhouette với ít nhất k=2 cụm.
    if len(df) < 30:
        raise HTTPException(
            422,
            f"Too few data points after processing ({len(df)} daily rows). Need at least 30.",
        )

    _upload["raw_df"] = raw_df
    _upload["detection"] = detection
    _upload["filename"] = file.filename
    _upload["daily_rows"] = len(df)
    _upload["date_range"] = {
        "start": df.iloc[0]["Date"].strftime("%Y-%m-%d"),
        "end": df.iloc[-1]["Date"].strftime("%Y-%m-%d"),
    }

    return {
        "filename": file.filename,
        "original_rows": len(raw_df),
        "daily_rows": len(df),
        "detected": {
            "date_col": detection["date_col"],
            "close_col": detection["close_col"],
            "is_unix_timestamp": detection["is_unix_timestamp"],
        },
        "date_range": _upload["date_range"],
    }


@app.delete("/api/upload")
def clear_upload():
    _upload["raw_df"] = None
    _upload["detection"] = None
    _upload["filename"] = None
    _upload["daily_rows"] = 0
    _upload["date_range"] = None
    return {"status": "cleared"}


# ---------------------------------------------------------------------------
# Endpoint phân tích
# ---------------------------------------------------------------------------

@app.get("/api/elbow")
def get_elbow(k_max: int = 10, window: int = 7, use_uploaded: bool = False):
    """Giai đoạn 2: Phương pháp Elbow + Silhouette để chọn K."""
    _, X, _, _ = _get_data(use_uploaded, window)
    return {"data": find_optimal_k(X, k_max=k_max)}


@app.get("/api/analysis")
def get_analysis(k: int = 4, model: str = "kmeans", window: int = 7, use_uploaded: bool = False):
    """Giai đoạn 3-5: huấn luyện mô hình, diễn giải cụm, trả về toàn bộ dữ liệu hiển thị."""
    df, X, _, scaler = _get_data(use_uploaded, window)

    if model == "gmm":
        labels, _, cluster_names, sil, _, X_pca = run_gmm(X, k, scaler)
        extra: dict = {}
    else:
        labels, _, cluster_names, sil, inertia, X_pca = run_kmeans(X, k, scaler)
        extra = {"inertia": inertia}

    # Dữ liệu giá theo ngày kèm nhãn cụm
    price_data = []
    for i, (_, row) in enumerate(df.iterrows()):
        cid = int(labels[i])
        price_data.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "close": float(row["Close"]),
            "cluster": cid,
            "cluster_name": cluster_names[cid],
            "log_return": float(row["log_return"]),
            "volatility": float(row["volatility"]),
            "momentum": float(row["momentum"]),
        })

    # Vùng chế độ liên tiếp để tô màu nền biểu đồ
    regions: list[dict] = []
    if len(labels) > 0:
        cur = int(labels[0])
        start = 0
        for i in range(1, len(labels)):
            if int(labels[i]) != cur:
                regions.append({
                    "start": df.iloc[start]["Date"].strftime("%Y-%m-%d"),
                    "end": df.iloc[i - 1]["Date"].strftime("%Y-%m-%d"),
                    "cluster": cur,
                    "cluster_name": cluster_names[cur],
                })
                cur = int(labels[i])
                start = i
        regions.append({
            "start": df.iloc[start]["Date"].strftime("%Y-%m-%d"),
            "end": df.iloc[-1]["Date"].strftime("%Y-%m-%d"),
            "cluster": cur,
            "cluster_name": cluster_names[cur],
        })

    # Biểu đồ phân tán PCA 2D
    pca_data = [
        {
            "x": float(X_pca[i, 0]),
            "y": float(X_pca[i, 1]),
            "cluster": int(labels[i]),
            "cluster_name": cluster_names[int(labels[i])],
            "date": df.iloc[i]["Date"].strftime("%Y-%m-%d"),
        }
        for i in range(len(X_pca))
    ]

    # Giai đoạn 4: thống kê cụm
    cluster_stats = []
    for cid, cname in sorted(cluster_names.items()):
        mask = labels == cid
        cdf = df[mask]
        cluster_stats.append({
            "id": cid,
            "name": cname,
            "count": int(mask.sum()),
            "pct": round(float(mask.sum() / len(labels) * 100), 1),
            "avg_return": float(cdf["log_return"].mean()),
            "avg_volatility": float(cdf["volatility"].mean()),
            "avg_momentum": float(cdf["momentum"].mean()),
        })

    return {
        "price_data": price_data,
        "regions": regions,
        "pca_data": pca_data,
        "cluster_stats": cluster_stats,
        "silhouette_score": sil,
        "model": model,
        "k": k,
        "total_days": len(df),
        "date_range": {
            "start": df.iloc[0]["Date"].strftime("%Y-%m-%d"),
            "end": df.iloc[-1]["Date"].strftime("%Y-%m-%d"),
        },
        **extra,
    }
