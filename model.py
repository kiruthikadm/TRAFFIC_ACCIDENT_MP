import pandas as pd
from sklearn.cluster import KMeans

def run_kmeans():
    df = pd.read_csv("dataset/cleaned_data.csv")

    X = df[["latitude", "longitude"]]

    # Apply KMeans
    kmeans = KMeans(n_clusters=5, random_state=42)
    df["cluster"] = kmeans.fit_predict(X)

    # Save clustered data
    df.to_csv("dataset/clustered_data.csv", index=False)

    return df