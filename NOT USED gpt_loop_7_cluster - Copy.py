import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
import chromadb
from sklearn.preprocessing import normalize

def main():
    # Define the directory where chromadb is stored and the collection name.
    chromadb_dir = "chromadb_dir"
    collection_name = "radiation_hardening_15"
    
    # Connect to the Chroma DB using the directory.
    client = chromadb.PersistentClient(path=chromadb_dir)
    collection = client.get_collection(name=collection_name)
    
    # Retrieve keys 'documents' and 'embeddings' to the collection data 
    data = collection.get(include=['embeddings', 'documents'])

    documents = data.get('documents', [])
    embeddings = data.get('embeddings', [])
    
    print(f"Found {len(documents)} documents and {len(embeddings)} embeddings")

    if len(documents)==0 or len(embeddings)==0:
        print("No documents or embeddings found in the collection.")
        return
    
    # Convert embeddings into a numpy array for clustering.
    #X = np.array(embeddings)
    
    X = normalize(np.array(embeddings))
    
    # Configure DBSCAN. Adjust eps and min_samples parameters as needed.
    # Here we use cosine distance which can be useful for embeddings.
    dbscan = DBSCAN(eps=0.5, min_samples=5, metric='cosine')
    clusters = dbscan.fit_predict(X)
    
    # Create a DataFrame with the documents and their assigned cluster labels.
    df_output = pd.DataFrame({'documents': documents, 'clusters': clusters})
    
    # Export the results to an Excel file.
    output_filename = "radiation_hardening_clusters.xlsx"
    df_output.to_excel(output_filename, index=False)
    
    print(f"Output exported to {output_filename}")

if __name__ == "__main__":
    main()
