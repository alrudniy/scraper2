import chromadb

def list_collections():
    chromadb_dir = "chromadb_dir"
    
    # Connect to the ChromaDB persistent client
    client = chromadb.PersistentClient(path=chromadb_dir)
    
    # Get all collections names from the client
    collections = client.list_collections()
    
    # Print out the name of each collection
    if collections:
        
        print(collections)
       
    else:
        print("No collections found in chromadb.")

    collection_name = 'radiation_hardening_15'

    
    collection = client.get_collection(name=collection_name)
    # Get collection data, which includes the list of documents.

    collection_data = collection.get(include=['embeddings', 'documents', 'metadatas'])
    
    
    # Count the documents.
    
    documents = collection_data.get('documents', [])
    embeddings = collection_data.get('embeddings', [])



    print('-'*100)
    print("Columns in collection:")
    for key in collection_data.keys():
        print(key)
    print('-'*100)
    # Print the fetched results
    
    #print(collection_data)
    print(f"documents {documents}")
    print('-'*100)
    print(f"embeddings {embeddings}")
    print('-'*100)
    print(f"Found {len(documents)} documents in collection {collection_name}")
    print(f"Found {len(embeddings)} embeddings in collection {collection_name}")
if __name__ == "__main__":
    list_collections()
