import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import matplotlib.pyplot as plt


def pick_k(X, k_min=2, k_max=8, random_state=42):
    best_k, best_s = None, -1
    for k in range(k_min, k_max + 1):
        model = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
        labels = model.fit_predict(X)
        s = silhouette_score(X, labels)
        if s > best_s:
            best_k, best_s = k, s
    return best_k, best_s


def top_terms_df(vectorizer, kmeans, topn=12):
    """
    클러스터 센터의 가중치 기준 Top terms를 DataFrame으로 반환
    """
    terms = np.array(vectorizer.get_feature_names_out())
    centers = kmeans.cluster_centers_

    rows = []
    for c in range(centers.shape[0]):
        top_idx = centers[c].argsort()[::-1][:topn]
        for rank, j in enumerate(top_idx, 1):
            rows.append({
                "cluster": c,
                "rank": rank,
                "term": terms[j],
                "weight": float(centers[c][j]),
            })

    return pd.DataFrame(rows).sort_values(["cluster", "rank"])


def plot_cluster_counts(df):
    counts = df["cluster"].value_counts().sort_index()
    plt.figure()
    plt.bar(counts.index.astype(str), counts.values)
    plt.xlabel("cluster")
    plt.ylabel("count")
    plt.title("Cluster sizes (document counts)")
    plt.tight_layout()
    plt.show()


def main():
    df = pd.read_csv("data/hf_trending.csv").fillna("")
    df["text"] = (df["title"] + ". " + df["abstract"]).str.strip()

    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
    X = vec.fit_transform(df["text"])

    if len(df) < 3:
        print("Not enough documents to cluster. Need at least 3 rows.")
        return

    k_max = min(8, len(df) - 1)
    k, sil = pick_k(X, 2, k_max)
    print(f"chosen k={k}, silhouette={sil:.3f}")

    km = KMeans(n_clusters=k, n_init="auto", random_state=42)
    df["cluster"] = km.fit_predict(X)

    # (선택) 클러스터 크기만 간단히
    plot_cluster_counts(df)

    #  클러스터별 키워드(핵심 결과)
    kw_df = top_terms_df(vec, km, topn=12)

    # 콘솔 출력(클러스터별로 보기 좋게)
    print("\n" + "=" * 80)
    print("Top keywords per cluster")
    print("=" * 80)
    for c in range(k):
        terms = kw_df[kw_df["cluster"] == c]["term"].tolist()
        print(f"Cluster {c}: " + ", ".join(terms))

    # 저장
    df.to_csv("data/hf_trending_clustered.csv", index=False)
    kw_df.to_csv("data/hf_trending_cluster_keywords.csv", index=False)

    print("\nsaved -> data/hf_trending_clustered.csv")
    print("saved -> data/hf_trending_cluster_keywords.csv")


if __name__ == "__main__":
    main()
