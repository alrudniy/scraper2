import json
import sys
from openpyxl import load_workbook
import json
import sys
from time import sleep
from pgpt_python.client import PrivateGPTApi
from collections import Counter
#import chromadb
#from chromadb.config import Settings
import json
from datetime import datetime
import uuid
from langchain_chroma import Chroma

def main(json_file, client):
    with open(json_file, 'r') as f:
        data = json.load(f)

    
    collection_name = json_file.replace('.', '_')
    if len(collection_name) > 63:
        collection_name = collection_name[:63]

    # Initialize the Chroma database client with persistent storage.
    settings = Settings(persist_directory="chromadb_dir")
    chroma_client = chromadb.Client(settings=settings)
    collection = chroma_client.get_or_create_collection(name=collection_name)
    # Initialize the Chroma vector store with persistent storage.

    # Loop through each key (phrase) in the dictionary.
    for phrase in data.keys():
        # Generate the embedding for the phrase.
        embedding_result = client.embeddings.embeddings_generation(input=phrase)
        embedding = embedding_result.data[0].embedding

        # Add the phrase and its embedding to the Chroma collection.
        collection.add(
            documents=[phrase],
            ids=[str(uuid.uuid4())],
            embeddings=[embedding]
            
        )
        print(f"{phrase} --> {collection_name}")

    print("All phrase embeddings have been stored in the Chroma database at 'chromadb_dir'.")
    
    # get  collections
    existing_collections = chroma_client.list_collections()
    #collection_names = [col.name for col in existing_collections]
    print(f"Existing collections: {existing_collections}")

    # save to disk
    #chroma_client.persist()
    



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gpt_loop_5_group.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=600000)
    main(json_file, client)
