import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


def interpret_clusters(centroids_orig: np.ndarray) -> dict[int, str]:
    """
    Gán nhãn chế độ thị trường bằng cách xếp hạng các centroid theo lợi nhuận và độ biến động.
    Đặc trưng: [log_return, volatility, momentum]

    Nhãn được gán theo thứ tự ưu tiên tham lam (Tăng → Giảm → Biến động cao)
    để các chế độ đặc trưng nhất luôn nhận được tên có ý nghĩa nhất,
    bất kể người dùng chọn bao nhiêu cụm K.
    """
    k = centroids_orig.shape[0]
    remaining = list(range(k))
    names: dict[int, str] = {}

    returns = centroids_orig[:, 0]
    vols = centroids_orig[:, 1]

    def pick(lst, arr, fn):
        # fn là np.argmax hoặc np.argmin áp dụng lên *tập con* của arr được đánh chỉ số bởi lst,
        # sau đó ánh xạ về chỉ số centroid gốc.
        vals = [arr[i] for i in lst]
        idx = lst[int(fn(vals))]
        lst.remove(idx)
        return idx

    # Tăng mạnh: lợi nhuận cao nhất
    names[pick(remaining, returns, np.argmax)] = "Bull Market"
    if not remaining:
        return names

    # Giảm mạnh: lợi nhuận thấp nhất (âm nhất)
    names[pick(remaining, returns, np.argmin)] = "Bear Market"
    if not remaining:
        return names

    # Biến động cao: độ biến động cao nhất trong số còn lại
    names[pick(remaining, vols, np.argmax)] = "High Volatility"

    # Các cụm thừa ngoài ba chế độ chuẩn sẽ nhận nhãn chuyển tiếp tổng quát.
    extras = ["Sideways", "Weak Bull", "Weak Bear", "Transition", "Range Bound"]
    for j, idx in enumerate(remaining):
        names[idx] = extras[j] if j < len(extras) else f"Cluster {idx}"

    return names


def find_optimal_k(X: np.ndarray, k_max: int = 10) -> list[dict]:
    """Giai đoạn 2: Phương pháp Elbow + Điểm Silhouette để xác định K tối ưu."""
    results = []
    for k in range(2, k_max + 1):
        # n_init=10: chạy 10 lần khởi tạo ngẫu nhiên và giữ inertia tốt nhất,
        # giảm nguy cơ hội tụ về cực trị cục bộ kém.
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        results.append({
            "k": k,
            "inertia": float(km.inertia_),
            "silhouette": float(silhouette_score(X, labels)),
        })
    return results


def _pca2d(X: np.ndarray) -> np.ndarray:
    """Giai đoạn 5: Giảm chiều xuống 2D để hiển thị biểu đồ phân tán."""
    return PCA(n_components=2, random_state=42).fit_transform(X)


def run_kmeans(X: np.ndarray, k: int, scaler):
    """Giai đoạn 3: Phân cụm K-Means."""
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    # Biến đổi ngược centroid về thang đặc trưng gốc để interpret_clusters
    # so sánh giá trị lợi nhuận/biến động thực, không phải z-score.
    centroids = scaler.inverse_transform(km.cluster_centers_)
    cluster_names = interpret_clusters(centroids)
    sil = float(silhouette_score(X, labels))
    return labels, centroids, cluster_names, sil, float(km.inertia_), _pca2d(X)


def run_gmm(X: np.ndarray, k: int, scaler):
    """Giai đoạn 3: Mô hình hỗn hợp Gaussian (phân cụm mềm).

    GMM gán mỗi điểm vào thành phần có xác suất cao nhất (nhãn cứng để hiển thị),
    nhưng mô hình nền tảng mang tính xác suất — hữu ích khi ranh giới cụm chồng lấn.
    Inertia không được định nghĩa cho GMM, nên trả về None ở vị trí đó.
    """
    gmm = GaussianMixture(n_components=k, random_state=42, n_init=5)
    gmm.fit(X)
    labels = gmm.predict(X)
    centroids = scaler.inverse_transform(gmm.means_)
    cluster_names = interpret_clusters(centroids)
    sil = float(silhouette_score(X, labels))
    return labels, centroids, cluster_names, sil, None, _pca2d(X)
