import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Toggle
USE_LOCAL_MODELS = os.getenv("USE_LOCAL_MODELS", "true").lower() == "true"

# Paths
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "").strip('"').strip("'")
CHROMA_DB_PATH = "./chroma_store"
COLLECTION_NAME = "second_brain"

# Models
if USE_LOCAL_MODELS:
    EMBED_MODEL = "nomic-embed-text"
    LLM_MODEL = "llama3.2:1b"
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBED_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o"