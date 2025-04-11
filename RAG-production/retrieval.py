import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("anthropic_doc")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")
)

query_engine = index.as_query_engine(similarity_top_k=7)
response = query_engine.query("What is d/f b/w workflows and agents?")
print("\n\nHere is the response:\n\n", response, "\n\n")

