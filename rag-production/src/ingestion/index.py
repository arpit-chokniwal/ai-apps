from llama_index.core import SimpleDirectoryReader
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor

from llama_index.core.node_parser import SentenceSplitter

from llama_index.core.ingestion import IngestionPipeline

from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext

from utils import file_extractor
from configure_models import get_hf_embedding_model, get_gemini_llm
from vector_database import get_vector_store

def read_docs(path="src/ingestion/docs"):
    try:
        doc_reader = SimpleDirectoryReader(input_dir=path, file_extractor=file_extractor())
        docs = doc_reader.load_data()
        print(f"Loaded {len(docs)} documents")
        return docs
    except Exception as e:
        print(f"Error reading documents: {e}")
        raise


def transform_docs(documents, llm):
    try:
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
        metadata_extractors = [
            TitleExtractor(llm=llm), 
            QuestionsAnsweredExtractor(llm=llm)
        ]

        pipeline = IngestionPipeline(transformations=[
            SentenceSplitter(chunk_overlap=120), # SentenceSplitter is a text parsing tool that splits text into chunks while trying to preserve complete sentences and paragraphs together, avoiding partial sentences at chunk boundaries.
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


def index_and_store_nodes(vector_store, nodes, embed_model):
    try:
        # assign chroma as the vector_store to the context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        stored_index = VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)
        print("Successfully indexed and stored nodes")
        return stored_index
    except Exception as e:
        print(f"Error indexing and storing nodes: {e}")
        raise


def indexing_process(embed_model, llm, path="src/ingestion/docs", collection_name="anthropic_doc", db_path="chroma-db"):
    print("Starting document indexing process")
    documents = read_docs(path)
    nodes = transform_docs(documents, llm)
    vector_store = get_vector_store(db_path, collection_name)
    index = index_and_store_nodes(vector_store, nodes, embed_model)
    print("Document indexing process completed successfully")
    return index


# Ignore this it is for testing the RAG 
# def ask_rag(query, collection_name="anthropic_doc", db_path="chroma-db", embed_model=get_hf_embedding_model(), llm=get_gemini_llm()):
#     vector_store = get_vector_store(db_path, collection_name)
#     index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
#     response = index.as_query_engine(similarity_top_k=7, llm=llm).query(query)
#     print("\nResponse: \n", response, "\n\n")
#     return response



if __name__ == "__main__":
    # response = ask_rag("What is the difference between workflows and agents?")
    indexing_process(embed_model=get_hf_embedding_model(), llm=get_gemini_llm())
