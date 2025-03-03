import json
import sys
import uuid
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from chromadb import Documents, EmbeddingFunction, Embeddings
#from langchain.embeddings import HuggingFaceEmbeddings
#from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from chromadb.utils import embedding_functions

from langchain.embeddings.huggingface import HuggingFaceEmbeddings

# Wrap LangChain’s HuggingFaceEmbeddings into an EmbeddingFunction for Chromadb
class HFEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_kwargs, encode_kwargs, model_name: str = "BAAI/bge-large-en-v1.5"):
        model_kwargs = {'device': 'cuda'}
        encode_kwargs = {'normalize_embeddings': False}
        self.embedder = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
    
    def __call__(self, texts: Documents) -> Embeddings:
        # texts is expected to be a list of strings
        return self.embedder.embed_documents(texts)





def main(json_file):
    # 1. Load JSON
    with open(json_file, "r") as f:
        data = json.load(f)

    # 2. Collection name
    collection_name = "radiation_hardening_10"

    # 3. Make a persistent client
    persistent_client = chromadb.PersistentClient(path="chromadb_dir")

    # 4. Build your documents list + unique IDs
    documents = list(data.keys())
    document_ids = [f"id{i}" for i in range(len(documents))]

    # 5. Manually create embeddings (LangChain)
    #embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'normalize_embeddings': False}
    )
    document_embeddings = embeddings.embed_documents(documents)

    print(document_embeddings[:5])

    # 6. Get the dimension of your vectors
    dimension = len(document_embeddings[0])

    # 7. Create or get the collection, specifying the dimension (no embedding_function)
    collection = persistent_client.get_or_create_collection(
        name=collection_name
        # , dimension=dimension  # crucial if you manually supply embeddings!
    )

    # 8. Add docs, IDs, and your manually computed embeddings
    collection.add(documents=documents, ids=document_ids, embeddings=document_embeddings)

    print("All phrase embeddings have been stored in the Chroma DB at 'chromadb_dir'.")





if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    main(json_file)
