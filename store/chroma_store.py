import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from config import CHROMA_DB_PATH, COLLECTION_NAME

# Initialize vector store for LlamaIndex
def get_vector_store():
  # A persistent client stores embeddings in CHROMA_DB_PATH
  client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
  collection = client.get_or_create_collection(COLLECTION_NAME)
  vector_store = ChromaVectorStore(chroma_collection=collection)
  return vector_store

def get_storage_context():
  vector_store = get_vector_store()
  return StorageContext.from_defaults(vector_store=vector_store)
