# Data Flow — Market Trend Analyzer Backend

This document traces how raw CSV data moves through each Python function before the
result is sent back to the client. There are two entry paths depending on whether the
default built-in dataset or a user-uploaded file is used. Both paths converge at the
same feature-engineering and clustering pipeline.

---

## Overview of modules

| File | Responsibility |
|---|---|
| `main.py` | FastAPI routes, in-memory upload store, response assembly |
| `column_detector.py` | Auto-detect date and price columns from an unknown CSV |
| `data_processor.py` | Load CSV → clean → engineer features → standardise |
| `clustering.py` | K-Means / GMM training, elbow search, PCA projection, cluster labelling |

---

## Path 1 — Default dataset (`coin_Bitcoin.csv`)

```
Client
  │
  ├─ GET /api/elbow?use_uploaded=false&window=7&k_max=10
  └─ GET /api/analysis?use_uploaded=false&window=7&k=4&model=kmeans
         │
         ▼
    main.py :: _get_data(use_uploaded=False, window)
         │  use_uploaded is False  →  takes the default branch
         ▼
    data_processor.py :: load_and_process(window)
         │
         │  1. pd.read_csv("../dataset/coin_Bitcoin.csv")
         │     raw shape: (N rows, many cols including "Date", "Close")
         │
         │  2. df["Date"] = pd.to_datetime(df["Date"])
         │     converts string dates → datetime64
         │
         │  3. df.sort_values("Date").reset_index()
         │     rows ordered oldest → newest
         │
         ▼
    data_processor.py :: _engineer_features(df, window)   ← shared pipeline
```

---

## Path 2 — User-uploaded file

### Phase A  —  Upload  (`POST /api/upload`)

```
Client
  └─ POST /api/upload   (multipart CSV file)
         │
         ▼
    main.py :: upload_dataset(file)
         │
         │  1. Validate extension (.csv only)
         │  2. Read raw bytes; reject if > 500 MB
         │  3. pd.read_csv(bytes)  →  raw_df  (all original columns kept)
         │  4. Reject if raw_df is empty
         │
         ▼
    column_detector.py :: detect_columns(raw_df)
         │
         │  Returns a dict:
         │    date_col          — name of the date/timestamp column
         │    close_col         — name of the close/price column
         │    is_unix_timestamp — True if the date column holds integers
         │    is_unix_ms        — True if those integers are millisecond epochs
         │
         │  Detection strategy (in order):
         │    a. Match column names against _DATE_KEYWORDS / _CLOSE_KEYWORDS
         │       (priority-ordered lists, case-insensitive)
         │    b. Fallback: any column name that contains "date", "time", "stamp"
         │    c. Fallback for close: numeric columns not in _EXCLUDE_FROM_CLOSE;
         │       prefer names containing "close"/"price"; last resort = rightmost numeric
         │    d. Unix detection: if date_col is numeric dtype,
         │       sample > 1e12 → milliseconds, else seconds
         │
         ▼
    main.py :: upload_dataset  (validation run)
         │
         │  Calls process_uploaded(raw_df, detection, window=7) once
         │  just to count daily rows after processing.
         │  Rejects the file if result has < 30 daily rows.
         │
         │  On success, stores in module-level _upload dict:
         │    _upload["raw_df"]     = raw_df       (full original DataFrame)
         │    _upload["detection"]  = detection    (column mapping)
         │    _upload["filename"]   = file.filename
         │    _upload["daily_rows"] = len(processed df)
         │    _upload["date_range"] = {start, end} strings
         │
         ▼
    Response to client:
         {
           filename, original_rows, daily_rows,
           detected: { date_col, close_col, is_unix_timestamp },
           date_range: { start, end }
         }
```

### Phase B  —  Analysis with uploaded data

```
Client
  └─ GET /api/analysis?use_uploaded=true&window=7&k=4&model=kmeans
         │
         ▼
    main.py :: _get_data(use_uploaded=True, window)
         │  _upload["raw_df"] is not None  →  takes the upload branch
         ▼
    data_processor.py :: process_uploaded(raw_df, detection, window)
         │
         │  1. Extract only [date_col, close_col] from raw_df
         │     rename columns → ["Date", "Close"]
         │
         │  2. pd.to_numeric(df["Close"], errors="coerce")
         │     non-numeric price values become NaN
         │
         │  3. Parse dates:
         │     if is_unix_timestamp:
         │       unit = "ms" or "s"
         │       pd.to_datetime(df["Date"], unit=unit, utc=True).dt.tz_localize(None)
         │     else:
         │       pd.to_datetime(df["Date"])
         │
         │  4. Sort by Date, drop rows where Close is NaN
         │
         │  5. Sub-daily detection:
         │     compute median interval between consecutive rows
         │     if median_interval < 20 hours:
         │       resample Close to daily frequency using .last()
         │       (e.g. 1-minute BTC data → one row per calendar day)
         │
         ▼
    data_processor.py :: _engineer_features(df, window)   ← shared pipeline
```

---

## Shared pipeline — `_engineer_features(df, window)`

Both paths feed a clean daily DataFrame with columns `[Date, Close]` into this function.

```
Input df:
  Date (datetime64)  |  Close (float)
  -------------------|----------------
  2017-11-09         |  7143.58
  2017-11-10         |  6618.14
  ...                |  ...

Step 1 — Drop rows where Close is NaN

Step 2 — Compute features (all added as new columns to df):

  log_return   = ln(Close_t / Close_{t-1})
                 → daily percentage change on log scale

  volatility   = rolling(window).std(log_return)
                 → short-window price risk  [used in model]

  volatility_14= rolling(14).std(log_return)
                 → fixed 14-day risk  [kept in df, not in model]

  momentum     = (Close_t - Close_{t-window}) / Close_{t-window}
                 → short-window rate of change  [used in model]

  momentum_30  = (Close_t - Close_{t-30}) / Close_{t-30}
                 → fixed 30-day rate of change  [kept in df, not in model]

Step 3 — df.dropna()
  Removes the first `max(window, 30)` rows that have NaN from rolling/shift ops.

Step 4 — Build feature matrix
  feature_cols = ["log_return", "volatility", "momentum"]
  X  = df[feature_cols].values          shape: (N, 3)  raw scale

Step 5 — StandardScaler
  X_scaled = scaler.fit_transform(X)    shape: (N, 3)  mean=0, std=1
  (scaler is returned so centroids can be inverse-transformed later)

Output:
  df       — DataFrame with Date, Close, and all feature columns
  X_scaled — numpy array (N, 3), standardised
  feature_cols — ["log_return", "volatility", "momentum"]
  scaler   — fitted StandardScaler instance
```

---

## Elbow endpoint  (`GET /api/elbow`)

```
_get_data(...)  →  (df, X_scaled, feature_cols, scaler)
                          │
                          │  only X_scaled is used
                          ▼
clustering.py :: find_optimal_k(X_scaled, k_max)

  for k in range(2, k_max + 1):
    KMeans(n_clusters=k, n_init=10).fit_predict(X_scaled)
    record inertia and silhouette_score

  Returns list of dicts:
    [ { k: 2, inertia: ..., silhouette: ... },
      { k: 3, inertia: ..., silhouette: ... },
      ...
      { k: k_max, inertia: ..., silhouette: ... } ]

Response to client:
  { "data": [ { k, inertia, silhouette }, ... ] }
```

---

## Analysis endpoint  (`GET /api/analysis`)

```
_get_data(...)  →  (df, X_scaled, feature_cols, scaler)
                          │
               ┌──────────┴──────────┐
          model=kmeans          model=gmm
               │                    │
               ▼                    ▼
  clustering.py ::         clustering.py ::
  run_kmeans(X, k, scaler) run_gmm(X, k, scaler)
               │                    │
               │  KMeans(n_clusters=k, n_init=10)
               │  GaussianMixture(n_components=k, n_init=5)
               │
               │  Both produce:
               │    labels    — array (N,)  integer cluster id per day
               │    centroids — array (k, 3) inverse-transformed to original scale
               │    sil       — float  silhouette score
               │    X_pca     — array (N, 2) via _pca2d below
               │    inertia   — float (KMeans only; None for GMM)
               │
               ▼
  clustering.py :: interpret_clusters(centroids)
    Greedy label assignment in priority order:
      1. Highest log_return centroid  → "Bull Market"
      2. Lowest  log_return centroid  → "Bear Market"
      3. Highest volatility centroid  → "High Volatility"
      4. Remaining (if k > 3)         → "Sideways", "Weak Bull", ...

    Returns dict: { cluster_id: "label name", ... }

  clustering.py :: _pca2d(X_scaled)
    PCA(n_components=2).fit_transform(X_scaled)
    Projects all N days onto 2 principal components for scatter plot.

               │
               ▼
  main.py :: get_analysis  (assembles the response)

    price_data  — one entry per day:
                  { date, close, cluster, cluster_name,
                    log_return, volatility, momentum }

    regions     — contiguous date spans of the same cluster,
                  used by the frontend to draw background colour bands:
                  [ { start, end, cluster, cluster_name }, ... ]

    pca_data    — one entry per day in PCA space:
                  { x, y, cluster, cluster_name, date }

    cluster_stats — one entry per cluster:
                  { id, name, count, pct,
                    avg_return, avg_volatility, avg_momentum }

Response to client:
  {
    price_data, regions, pca_data, cluster_stats,
    silhouette_score, model, k, total_days, date_range,
    inertia  (KMeans only)
  }
```

---

## State between requests

The module-level `_upload` dict in `main.py` acts as a single-session store.
It holds the original `raw_df` (not the processed one) so that every analysis
request can re-run `process_uploaded` with a different `window` parameter
without requiring the user to re-upload the file.

```
POST /api/upload        → stores raw_df + detection into _upload
GET  /api/elbow         → reads _upload["raw_df"], reprocesses with requested window
GET  /api/analysis      → reads _upload["raw_df"], reprocesses with requested window
DELETE /api/upload      → clears all fields in _upload back to None
GET  /api/upload/info   → returns metadata from _upload (no reprocessing)
```
