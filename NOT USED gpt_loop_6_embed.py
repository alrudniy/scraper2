import json
import sys
from pgpt_python.client import PrivateGPTApi
import uuid
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings

class PGPTEmbeddings(Embeddings):
    """A wrapper to use PrivateGPTApi's embedding generation with LangChain."""
    def __init__(self, client):
        self.client = client

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            # Generate the embedding for each document/phrase.
            result = self.client.embeddings.embeddings_generation(input=text)
            embeddings.append(result.data[0].embedding)
        return embeddings

    def embed_query(self, text):
        return self.embed_documents([text])[0]

def main(json_file, client):
    # Load data from the JSON file.
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Derive a collection name from the JSON file name.
    collection_name = json_file.replace('.', '_')
    if len(collection_name) > 63:
        collection_name = collection_name[:63]

    # Initialize our PGPT embeddings wrapper.
    pgpt_embeddings = PGPTEmbeddings(client)

    # Create a Chroma vectorstore with persistent storage.
    vectorstore = Chroma.from_texts(
        texts=list(data.keys()),
        embedding=pgpt_embeddings,
        collection_name=collection_name,
        persist_directory="chromadb_dir"
    )

    # For each phrase added, print a confirmation.
    for phrase in data.keys():
        print(f"{phrase} --> {collection_name}")

    print("All phrase embeddings have been stored in the Chroma database at 'chromadb_dir'.")
    # display the collection name to confirm its creation.
    #print(f"Vectorstore collection: {vectorstore.collection_name}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gpt_loop_5_group.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    # Initialize the PrivateGPT client with default settings.
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=600000)
    main(json_file, client)
