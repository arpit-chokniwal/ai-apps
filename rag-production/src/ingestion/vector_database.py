import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

def get_vector_store(db_path, collection_name):
    try:
        db = chromadb.PersistentClient(path=db_path)

        chroma_collection = db.get_or_create_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        print(f"Connected to vector store collection: {collection_name}")
        return vector_store
    except Exception as e:
        print(f"Error connecting to vector store: {e}")
        raise
