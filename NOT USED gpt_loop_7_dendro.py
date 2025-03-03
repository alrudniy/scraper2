import os
import numpy as np
from sklearn.preprocessing import normalize
import chromadb
from datetime import datetime
from sklearn.decomposition import PCA

import pandas as pd
import matplotlib.pyplot as plt

# New imports for hierarchical clustering
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

def plot_dendrogram(X, method='ward', truncate_mode=None, p=12):
    """
    Plots the dendrogram using hierarchical clustering.

    :param X: Numpy array of embeddings (or reduced embeddings).
    :param method: Linkage method to use ('ward', 'complete', 'average', 'single', etc.).
    :param truncate_mode: If you want to truncate the dendrogram (e.g. 'level' or 'lastp').
    :param p: The number of leaf nodes to show in truncated mode.
    """
    # Compute the linkage matrix
    Z = linkage(X, method=method)

    plt.figure(figsize=(10, 7))
    dendrogram(
        Z,
        truncate_mode=truncate_mode,  # None (full) or 'level'/'lastp'
        p=p,
        leaf_rotation=90.,
        leaf_font_size=12.,
    )
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Sample index')
    plt.ylabel('Distance (Ward)')
    plt.show()

    return Z

def perform_hierarchical_clustering(Z, num_clusters=None, distance_threshold=None):
    """
    Performs hierarchical clustering based on the linkage matrix Z.
    Either specify the number of clusters (num_clusters) or a distance threshold.

    :param Z: Linkage matrix from scipy.cluster.hierarchy.linkage
    :param num_clusters: Number of clusters to find.
    :param distance_threshold: Threshold to apply when forming flat clusters.
    :return: cluster_labels, array of cluster assignments for each data point.
    """
    if num_clusters:
        # cluster by specifying the max number of clusters
        cluster_labels = fcluster(Z, t=num_clusters, criterion='maxclust')
    elif distance_threshold:
        # cluster by specifying distance threshold
        cluster_labels = fcluster(Z, t=distance_threshold, criterion='distance')
    else:
        raise ValueError("Must provide either num_clusters or distance_threshold.")

    return cluster_labels


if __name__ == '__main__':
    chromadb_dir = "chromadb_dir"
    collection_name = "radiation_hardening_15"
    
    client = chromadb.PersistentClient(path=chromadb_dir)
    collection = client.get_collection(name=collection_name)
    
    data = collection.get(include=['embeddings', 'documents'])
    documents = data.get('documents', [])
    embeddings = data.get('embeddings', [])
    
    print(f"Found {len(documents)} documents and {len(embeddings)} embeddings")
    
    # If you want cosine-based distances, you could normalize first. 
    # Alternatively, for Ward's method, Euclidean distance is typical.
    X = np.array(embeddings)

    # (Optional) Reduce dimensionality with PCA, for speed and clarity of dendrogram
    pca = PCA(n_components=50, random_state=42)
    X_reduced = pca.fit_transform(X)

    # 1. Create and plot dendrogram
    Z = plot_dendrogram(
        X_reduced,
        method='ward',
        truncate_mode='level',  # Set to None if you want to see full dendrogram
        p=12
    )

    # 2. Decide on number of clusters (by visual inspection of dendrogram or other criterion).
    #    For example, let's hard-code 5 clusters. Adjust as needed.
    num_clusters = 5

    # 3. Perform hierarchical clustering and get cluster labels
    cluster_labels = perform_hierarchical_clustering(Z, num_clusters=num_clusters)

    # 4. Create a DataFrame with documents and cluster labels
    df = pd.DataFrame({'documents': documents, 'cluster': cluster_labels})

    # 5. Save results to Excel
    output_dir = "hierarchical_clustering"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(
        output_dir, 
        f"radiation_hardening_hierarchical_{num_clusters}_clusters_{timestamp}.xlsx"
    )
    df.to_excel(output_filename, index=False)

    print(f"Clustering results saved to {output_filename}")
