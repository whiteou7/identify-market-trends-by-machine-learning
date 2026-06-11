import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


def interpret_clusters(centroids_orig: np.ndarray) -> dict[int, str]:
    """
    Assign market regime labels by ranking centroids on return and volatility.
    Features: [log_return, volatility, momentum]
    """
    k = centroids_orig.shape[0]
    remaining = list(range(k))
    names: dict[int, str] = {}

    returns = centroids_orig[:, 0]
    vols = centroids_orig[:, 1]

    def pick(lst, arr, fn):
        vals = [arr[i] for i in lst]
        idx = lst[int(fn(vals))]
        lst.remove(idx)
        return idx

    # Bull: highest return
    names[pick(remaining, returns, np.argmax)] = "Bull Market"
    if not remaining:
        return names

    # Bear: lowest (most negative) return
    names[pick(remaining, returns, np.argmin)] = "Bear Market"
    if not remaining:
        return names

    # High Volatility: highest volatility among the rest
    names[pick(remaining, vols, np.argmax)] = "High Volatility"

    # Remaining clusters
    extras = ["Sideways", "Weak Bull", "Weak Bear", "Transition", "Range Bound"]
    for j, idx in enumerate(remaining):
        names[idx] = extras[j] if j < len(extras) else f"Cluster {idx}"

    return names


def find_optimal_k(X: np.ndarray, k_max: int = 10) -> list[dict]:
    """Phase 2: Elbow Method + Silhouette Score to determine optimal K."""
    results = []
    for k in range(2, k_max + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        results.append({
            "k": k,
            "inertia": float(km.inertia_),
            "silhouette": float(silhouette_score(X, labels)),
        })
    return results


def _pca2d(X: np.ndarray) -> np.ndarray:
    """Phase 5: Reduce to 2D for scatter visualization."""
    return PCA(n_components=2, random_state=42).fit_transform(X)


def run_kmeans(X: np.ndarray, k: int, scaler):
    """Phase 3: K-Means clustering."""
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    centroids = scaler.inverse_transform(km.cluster_centers_)
    cluster_names = interpret_clusters(centroids)
    sil = float(silhouette_score(X, labels))
    return labels, centroids, cluster_names, sil, float(km.inertia_), _pca2d(X)


def run_gmm(X: np.ndarray, k: int, scaler):
    """Phase 3: Gaussian Mixture Model (soft clustering)."""
    gmm = GaussianMixture(n_components=k, random_state=42, n_init=5)
    gmm.fit(X)
    labels = gmm.predict(X)
    centroids = scaler.inverse_transform(gmm.means_)
    cluster_names = interpret_clusters(centroids)
    sil = float(silhouette_score(X, labels))
    return labels, centroids, cluster_names, sil, None, _pca2d(X)
