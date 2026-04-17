
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from store.chroma_store import get_vector_store, get_storage_context
from pipeline.embedder import configure_embed_model
from config import OBSIDIAN_VAULT_PATH

# Reads, chunks, embeds
def build_obsidian_index():
    configure_embed_model()

    print(f"Loading notes from: {OBSIDIAN_VAULT_PATH}")
    documents = SimpleDirectoryReader(
        input_dir=OBSIDIAN_VAULT_PATH,
        required_exts=[".md"],
        recursive=True,
        filename_as_id=True,
    ).load_data()

    print(f"Loaded {len(documents)} notes")

    for doc in documents:
        file_path = doc.metadata.get("file_path", "")
        parts = file_path.replace(OBSIDIAN_VAULT_PATH, "").strip("/").split("/")
        vault_name = parts[0] if len(parts) > 1 else "unknown"

        doc.metadata["source"] = "obsidian"
        doc.metadata["vault"] = vault_name
        doc.metadata["file_name"] = doc.metadata.get("file_name", "unknown")
        doc.metadata["file_path"] = file_path
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    storage_context = get_storage_context()

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True
    )
    print("Obsidian vault indexed successfully")
    return index

# Opens existing ChromaDB index so re-embedding isn't necessary
def load_obsidian_index():
    configure_embed_model()
    vector_store = get_vector_store()
    storage_context = get_storage_context()
    return VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
	)
