from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv
from utils import file_extractor
import os

load_dotenv()

doc_reader = SimpleDirectoryReader(input_dir="src/ingestion/docs", file_extractor=file_extractor)
docs = doc_reader.load_data()


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

from llama_index.llms.google_genai import GoogleGenAI


llm = GoogleGenAI(
    model="gemini-2.0-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
)
"""
This LLM will be used to generate the metadata.
You can use any other LLM that you want.

Note: This LLM has no relation with genration of embeddings.
"""


from llama_index.core.node_parser import SentenceSplitter
"""
SentenceSplitter is a text parsing tool that splits text into chunks while trying to preserve complete sentences and paragraphs together, avoiding partial sentences at chunk boundaries.
"""


from llama_index.core.ingestion import IngestionPipeline

pipeline = IngestionPipeline(transformations=[SentenceSplitter(), TitleExtractor(llm=llm), QuestionsAnsweredExtractor(llm=llm)])


nodes = pipeline.run(
    documents=docs,
    in_place=True,
    show_progress=True,
)
""" 
in_place determines whether the transformations create a new list for transformed nodes (in_place=False) or modify the existing array of nodes directly (in_place=True). It defaults to True to modify nodes in place.
"""

from llama_index.core.schema import MetadataMode

print("\n\nEMBED", nodes[6].get_content(metadata_mode=MetadataMode.EMBED), "\n\n")
print("\n\nLLM", nodes[6].get_content(metadata_mode=MetadataMode.LLM), "\n\n")



# Create a new embedding model
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
hf_embeddings = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")

# Store the embeddings in a vector database
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext


# initialize client, setting path to save data
db = chromadb.PersistentClient(path="chroma_db")

# create collection
chroma_collection = db.get_or_create_collection("anthropic_doc")

# assign chroma as the vector_store to the context
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Store the embeddings in a vector database
index = VectorStoreIndex(nodes, storage_context=storage_context, embed_model=hf_embeddings)

