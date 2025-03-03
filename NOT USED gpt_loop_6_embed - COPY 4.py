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
    collection_name = "radiation_hardening_8"

    # 3. Create a Chromadb embedding function
    model_kwargs = {"device": "cuda"}
    encode_kwargs = {"normalize_embeddings": False}
    hf_embedding_func = HFEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5", model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

    # 4. Make a persistent client
    persistent_client = chromadb.PersistentClient(path="chromadb_dir")

    # 5. Build your documents list + unique IDs
    documents = list(data.keys())
    document_ids = [f"id{i}" for i in range(len(documents))]

    # 6. Create/Get the collection **with** the embedding function
    collection = persistent_client.get_or_create_collection(
        name=collection_name,
        embedding_function=hf_embedding_func,
    )

    # 7. Just add docs + IDs; Chroma uses hf_embedding_func internally
    collection.add(documents=documents, ids=document_ids)

    # # Initialize a Chroma instance with the original document
    db = Chroma.from_documents(
         collection_name=db_collection_name,
         documents=documents, ids=doc_ids,
         embedding=embeddings, 
         persist_directory="./data")
    
     db.persist()

    print("All phrase embeddings have been stored in the Chroma DB at 'chromadb_dir'.")




if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    main(json_file)
