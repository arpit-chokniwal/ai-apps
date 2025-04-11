import os
from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv
from utils import file_extractor
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
    # SummaryExtractor,
    # KeywordExtractor,
    # PydanticProgramExtractor
)
"""
We will add some metadata for the docs.
This will help us to improve the quality of the index.

1. TitleExtractor: Generates a document title by analyzing the first few nodes of content.
2. KeywordExtractor: Extracts key terms/phrases that best represent each node's content.
3. QuestionsAnsweredExtractor: Generates questions that can be specifically answered by each node's content.
4. SummaryExtractor: Creates summaries for nodes and can include summaries of previous/next sections.
5. PydanticProgramExtractor: Converts node content into structured data using Pydantic models.

Note: use these extractors to generate metadata for the docs based on your use case :), i am using title and questions for now
"""


from llama_index.core.node_parser import SentenceSplitter
"""
SentenceSplitter is a text parsing tool that splits text into chunks while trying to preserve complete sentences and paragraphs together, avoiding partial sentences at chunk boundaries.
"""

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import MetadataMode
from llama_index.llms.google_genai import GoogleGenAI

# Store the embeddings in a vector database
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext


load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

llm = GoogleGenAI(
    model="gemini-2.0-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
)
"""
This LLM will be used to generate the metadata.
You can use any other LLM that you want.

Note: This LLM has no relation with generation of embeddings.
"""

# Create a new embedding model
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
hf_embeddings = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")


def read_docs(path="src/ingestion/docs"):
    try:
        doc_reader = SimpleDirectoryReader(input_dir=path, file_extractor=file_extractor)
        docs = doc_reader.load_data()
        print(f"Loaded {len(docs)} documents")
        return docs
    except Exception as e:
        print(f"Error reading documents: {e}")
        raise


def transform_docs(documents):
    try:
        metadata_extractors = [
            TitleExtractor(llm=llm), 
            QuestionsAnsweredExtractor(llm=llm)
        ]

        pipeline = IngestionPipeline(transformations=[
            SentenceSplitter(chunk_overlap=120),
            *metadata_extractors
        ])
        
        nodes = pipeline.run(
            documents=documents,
            show_progress=True,
        )
        
        print(f"Transformed documents into {len(nodes)} nodes")
        return nodes
    except Exception as e:
        print(f"Error transforming documents: {e}")
        raise


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


def index_and_store_nodes(vector_store, nodes):
    try:
        # assign chroma as the vector_store to the context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        stored_index = VectorStoreIndex(nodes, storage_context=storage_context, embed_model=hf_embeddings)
        print("Successfully indexed and stored nodes")
        return stored_index
    except Exception as e:
        print(f"Error indexing and storing nodes: {e}")
        raise


def start_indexing_and_storing_docs(path="src/ingestion/docs", collection_name="anthropic_doc", db_path="chroma-db"):
    print("Starting document indexing process")
    documents = read_docs(path)
    nodes = transform_docs(documents)
    vector_store = get_vector_store(db_path, collection_name)
    index = index_and_store_nodes(vector_store, nodes)
    print("Document indexing process completed successfully")
    return index


if __name__ == "__main__":
    start_indexing_and_storing_docs()
