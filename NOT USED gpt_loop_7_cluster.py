import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
import chromadb

def main():
    chromadb_dir = "chromadb_dir"
    collection_name = "radiation_hardening_15"
    
    client = chromadb.PersistentClient(path=chromadb_dir)
    collection = client.get_collection(name=collection_name)
    
    data = collection.get(include=['embeddings', 'documents'])

    documents = data.get('documents', [])
    embeddings = data.get('embeddings', [])
    
    print(f"Found {len(documents)} documents and {len(embeddings)} embeddings")

    if len(documents) == 0 or len(embeddings) == 0:
        print("No documents or embeddings found in the collection.")
        return
    
    # Normalize embeddings if desired (can help with cosine similarity)
    X = normalize(np.array(embeddings))
    
    # *** Adjust these values: smaller eps for embeddings often helps ***
    eps = 0.196
    min_samples=3
    metric = 'cosine'
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
    clusters = dbscan.fit_predict(X)
    
    # Create a DataFrame with documents and their assigned cluster labels.
    df_output = pd.DataFrame({
        'documents': documents,
        'clusters': clusters
    })

    df_output.sort_values(by='clusters', ascending=False, inplace=True)

    output_filename = f"radiation_hardening_clusters_dbscan_eps={eps}_minsample={min_samples}_{metric}.xlsx"
    df_output.to_excel(output_filename, index=False)
    
    print(f"Output exported to {output_filename}")

if __name__ == "__main__":
    main()
