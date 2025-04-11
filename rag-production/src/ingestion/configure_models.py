import os
from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


load_dotenv()


def get_gemini_llm(model_name="gemini-2.0-flash"):
    """
    This LLM will be used to generate the metadata.
    You can use any other LLM that you want.

    Note: This LLM has no relation with generation of embeddings.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY environment variable is not set")

    llm = GoogleGenAI(
        model=model_name,
        api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return llm


def get_hf_embedding_model(model_name="BAAI/bge-large-en-v1.5"):
    """
    This embedding model will be used to generate the embeddings.
    You can use any other embedding model that you want.
    """
    return HuggingFaceEmbedding(model_name=model_name)

