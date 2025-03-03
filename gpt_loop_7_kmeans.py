import os
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
import chromadb
from datetime import datetime
from sklearn.decomposition import PCA

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# for automatically detecting the "elbow"
from kneed import KneeLocator

def compute_elbow_method(X, k_range=range(1, 100)):
    """Computes inertia for each k in the specified range."""
    inertia = []
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X)
        inertia.append(kmeans.inertia_)
    return inertia

def plot_elbow(k_range, inertia):
    """Plots the elbow curve for visual inspection."""
    plt.figure(figsize=(8, 4))
    plt.plot(list(k_range), inertia, 'bx-')
    plt.xlabel('Number of clusters')
    plt.ylabel('Inertia')
    plt.title('Elbow Method For Optimal k')
    plt.show()

def get_optimal_k(k_range, inertia):
    """Determines the optimal number of clusters using the KneeLocator."""
    kl = KneeLocator(list(k_range), inertia, curve="convex", direction="decreasing")
    return kl.elbow

def perform_kmeans(X, n_clusters):
    """Performs k-means clustering with the specified number of clusters."""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    return kmeans.fit_predict(X)

if __name__ == '__main__':
    chromadb_dir = "chromadb_dir"
    collection_name = "radiation_hardening_15"
    
    client = chromadb.PersistentClient(path=chromadb_dir)
    collection = client.get_collection(name=collection_name)
    
    data = collection.get(include=['embeddings', 'documents'])
    documents = data.get('documents', [])
    embeddings = data.get('embeddings', [])
    
    print(f"Found {len(documents)} documents and {len(embeddings)} embeddings")
    
    #if len(documents) == 0 or len(embeddings) == 0:
    #    print("No documents or embeddings found in the collection.")
        
    
    # Normalize embeddings for cosine similarity.
    #X = normalize(np.array(embeddings))
    X =np.array(embeddings)

    # Reduce dimensionality to, say, 50
    pca = PCA(n_components=50, random_state=42)
    X = pca.fit_transform(X)

    # ---------------------------------------------------------------------------------------

    # Use the elbow method to compute inertia for a range of cluster values
    k_range = range(1, 100)
    inertia = compute_elbow_method(X, k_range)
    plot_elbow(k_range, inertia)
    
    # Automatically determine the optimal k (or choose based on the plot)
    optimal_k = get_optimal_k(k_range, inertia)
    print("Optimal number of clusters determined by elbow method:", optimal_k)
    
     # Create a DataFrame with documents and their assigned cluster labels.
    df = pd.DataFrame({'documents': documents})

    # Fit k-means clustering with the optimal number of clusters
    df['cluster'] = perform_kmeans(X, optimal_k)
    
    # Create the output directory if it doesn't exist.
    output_dir = "kmeans"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(
                output_dir, 
                f"radiation_hardening_kmeans_{timestamp}.xlsx"
            )
            
    df.to_excel(output_filename, index=False)

    # visualize the clustering if working with 2D data
    #plt.figure(figsize=(8, 4))
    #plt.scatter(X.iloc[:, 0], X.iloc[:, 1], c=df['cluster'], cmap='viridis')
    #plt.xlabel('Feature 1')
    #plt.ylabel('Feature 2')
    #plt.title('KMeans Clustering')
    #plt.show()
