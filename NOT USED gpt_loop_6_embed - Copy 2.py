import json
import sys
import uuid
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from chromadb import Documents, EmbeddingFunction, Embeddings
#from langchain.embeddings import HuggingFaceEmbeddings
#from langchain_huggingface import HuggingFaceEmbeddings
import chromadb


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
    # 1. Load the JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # 2. Create a collection name from the JSON file (must not exceed 63 chars)
    #collection_name = json_file.replace('.', '_')
    #if len(collection_name) > 63:
    #    collection_name = collection_name[:60]

    collection_name = 'radiation_hardening_7'

    # 3. Initialize the HuggingFace embeddings using the specified model
    #embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    
    #model_kwargs = {'device': 'cuda'}
    #encode_kwargs = {'normalize_embeddings': False}
    #hf_embedding_func = HFEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5", model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'normalize_embeddings': False}
    )

    # 4. Initialize the Chroma vectorstore with the HuggingFace embeddings
    #vectorstore = Chroma(
        #collection_name=collection_name,
        #embedding_function=hf_embedding_func,
    #    persist_directory="chromadb_dir"
    #)
    persistent_client = chromadb.PersistentClient(path="chromadb_dir")
    

    
    documents = list(data.keys())
    print(f"docs: {documents}")
    # Every document needs an id for Chroma
    #document_ids = list(map(lambda tup: f"id{tup[0]}", enumerate(documents)))
    document_ids = [f"id{idx}" for idx, _ in enumerate(documents)]  
    
    #embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    document_embeddings = embeddings.embed_documents(documents)
    
    print(f"document_embeddings {document_embeddings}")

    #collection = vectorstore.get_or_create_collection( name=collection_name, embedding_function=hf_embedding_func())
    collection = persistent_client.get_or_create_collection(collection_name)
    
    #collection.add(documents=documents, ids=document_ids)
    collection.add(documents=documents, ids=document_ids, embeddings=document_embeddings)

    
    vector_store = Chroma(
        client=persistent_client,
        collection_name=collection_name,
        embedding_function=embeddings,
    )

    # 5. Loop through each key (phrase) in the JSON and add it to the store
    #for phrase in data.keys():
    #    vectorstore.add_texts(
    #        texts=[phrase],
    #        ids=[str(uuid.uuid4())]  # Unique ID for each phrase
    #    )
    #    print(f"Added phrase: {phrase} to collection: {collection_name}")

    print("All phrase embeddings have been stored in the Chroma database at 'chromadb_dir'.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    main(json_file)
