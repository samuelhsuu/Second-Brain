import chromadb

client = chromadb.PersistentClient(path="chroma_store")
collection = client.get_collection("second_brain")

# Search for any doc with "TSA" in the file name
results = collection.get(
    where={"source": "google_drive"},
    include=["metadatas"]
)

# 1. Added 'or []' in case results["metadatas"] is None
# 2. Wrapped m.get() in str() to prevent errors if file_name itself is None
tsa_docs = [
    m for m in (results["metadatas"] or []) 
    if "TSA" in str(m.get("file_name") or "")
] 

print(f"TSA documents in ChromaDB: {len(tsa_docs)}")
for doc in tsa_docs[:5]:
    print(doc)