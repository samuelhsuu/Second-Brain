from config import USE_LOCAL_MODELS, EMBED_MODEL
from llama_index.core import Settings

def configure_embed_model():
  if USE_LOCAL_MODELS:
    # Use ollama local embedding
    from llama_index.embeddings.ollama import OllamaEmbedding
    Settings.embed_model = OllamaEmbedding(model_name = EMBED_MODEL)
    print(f"Using local embedding model: {EMBED_MODEL}")
  """else:
    # Use OpenAI embedding
    from llama_index.embeddings.openai import OpenAIEmbedding
    import openai
    from config import OPENAI_API_KEY
    openai.api_key = OPENAI_API_KEY
    Settings.embed_model = OpenAIEmbedding(model = EMBED_MODEL)
    print(f"Using OpenAI embedding model: {EMBED_MODEL}")"""
