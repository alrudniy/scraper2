import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
import chromadb
from datetime import datetime

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
    
    # Create the output directory if it doesn't exist.
    output_dir = "output_DBSCAN"
    os.makedirs(output_dir, exist_ok=True)

    # Set constant parameters.
    min_samples = 3
    metric = 'cosine'

    # Prepare list to hold summary stats.
    summary_list = []

    # Loop over eps values from 0.1 to 0.5 (inclusive) with step 0.005.
    for eps in np.arange(0.1, 0.5001, 0.005):
        # Run DBSCAN with current eps.
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
        clusters = dbscan.fit_predict(X)
        
        # Create a DataFrame with documents and their assigned cluster labels.
        df_output = pd.DataFrame({
            'documents': documents,
            'clusters': clusters
        })
        
        # Sort the DataFrame by cluster labels in descending order.
        df_output.sort_values(by='clusters', ascending=False, inplace=True)
        
        # Build the filename and save the output DataFrame into the output_DBSCAN directory.
        output_filename = os.path.join(output_dir, 
            f"radiation_hardening_clusters_dbscan_eps={eps:.3f}_minsample={min_samples}_{metric}.xlsx")
        df_output.to_excel(output_filename, index=False)
        
        # Compute summary statistics.
        max_cluster = df_output['clusters'].max()
        min_cluster = df_output['clusters'].min()
        outlier_count = (df_output['clusters'] == -1).sum()
        
        # Append statistics to the summary list.
        summary_list.append({
            'eps': eps,
            'min_samples': min_samples,
            'metric': metric,
            'max_cluster': max_cluster,
            'min_cluster': min_cluster,
            'outlier_count': outlier_count
        })
        
        print(f"Processed eps={eps:.3f}. Output saved to {output_filename}")

    # Create a DataFrame from the summary statistics.
    df_summary = pd.DataFrame(summary_list)

    # Generate a timestamp and export the summary to a timestamped Excel file.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = os.path.join(output_dir, f"output_DBSCAN_{timestamp}.xlsx")
    df_summary.to_excel(summary_filename, index=False)

    print(f"Summary exported to {summary_filename}")

if __name__ == "__main__":
    main()
