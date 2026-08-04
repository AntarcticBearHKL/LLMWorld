import numpy as np
from sklearn.cluster import KMeans


def hourly_means(profile_watts):
    if len(profile_watts) < 1440:
        raise ValueError("负荷曲线长度不足 1440 分钟")
    hourly = []
    for h in range(24):
        seg = profile_watts[h * 60:(h + 1) * 60]
        hourly.append(sum(seg) / 60.0)
    return hourly


def normalize_shape(hourly):
    total = sum(hourly)
    if total <= 0:
        return [0.0] * len(hourly)
    return [v / total for v in hourly]


def load_factor(hourly):
    peak = max(hourly)
    mean = sum(hourly) / len(hourly)
    if peak <= 0:
        return 0.0
    return mean / peak


def peak_hour(hourly):
    return max(range(len(hourly)), key=lambda h: hourly[h])


def valley_hour(hourly):
    return min(range(len(hourly)), key=lambda h: hourly[h])


def peak_to_mean(hourly):
    peak = max(hourly)
    mean = sum(hourly) / len(hourly)
    if mean <= 0:
        return 0.0
    return peak / mean


def kmeans(features, k, seed=42, iters=300):
    data = np.asarray(features, dtype=float)
    n = len(data)
    if n < k:
        raise ValueError("样本数少于簇数")
    model = KMeans(n_clusters=k, init="k-means++", n_init=10,
                   max_iter=iters, random_state=seed)
    model.fit(data)
    labels = model.labels_.tolist()
    centers = model.cluster_centers_.tolist()
    wcss = float(model.inertia_)
    return labels, centers, wcss


def elbow_scores(features, k_max=8):
    n = len(features)
    scores = []
    for k in range(2, min(k_max, n) + 1):
        _, _, wcss = kmeans(features, k)
        scores.append({"k": k, "wcss": round(wcss, 4)})
    return scores


def auto_k(features, k_max=8):
    scores = elbow_scores(features, k_max)
    if not scores:
        return 2
    if len(scores) == 1:
        return scores[0]["k"]
    best_k = scores[0]["k"]
    best_gain = -1.0
    prev = scores[0]["wcss"]
    for s in scores[1:]:
        gain = prev - s["wcss"]
        if gain > best_gain:
            best_gain = gain
            best_k = s["k"]
        prev = s["wcss"]
    return best_k
