# Bitcoin Market Regime Classifier

Identifies Bitcoin market regimes (Bull, Bear, Sideways, High Volatility) from daily OHLCV data using unsupervised machine learning.

## Setup

Figure it out yourself

## Pipeline

| Phase | Description |
|-------|-------------|
| 1 | Feature engineering: Log Return, Volatility (rolling std), Momentum |
| 1 | StandardScaler normalization (required for K-Means / Euclidean distance) |
| 2 | Elbow Method + Silhouette Score to find optimal K |
| 3 | K-Means clustering (hard) and GMM (soft / probabilistic) |
| 4 | Cluster interpretation: label by centroid return & volatility |
| 5 | PCA 2D scatter + price chart with colored regime backgrounds |

## API

| Endpoint | Params | Description |
|----------|--------|-------------|
| `GET /api/elbow` | `k_max`, `window` | Inertia + Silhouette for K = 2…k_max |
| `GET /api/analysis` | `k`, `model`, `window` | Full analysis: price data, regions, PCA, cluster stats |

`model` accepts `kmeans` or `gmm`.
