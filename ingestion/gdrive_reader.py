import os
import io
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from store.chroma_store import get_storage_context, get_vector_store
from pipeline.embedder import configure_embed_model

# Request read permission
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

EXCLUDED_EXTENSIONS = {
    # Image types
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg',
	# File types
    '.zip', '.tar', '.gz', '.rar', '.7z', '.tgz'
}
EXCLUDED_KEYWORDS = {'dataset', 'training', 'images', 'photos', 'youtube'}

# File types to index
SUPPORTED_MIME_TYPES = {
	"application/vnd.google-apps.document" : "Google Doc",
	"application/pdf" : "PDF",
	"text/plain" : "Text",
	"text/markdown" : "Markdown"
}

# A GDoc isn't a real file - export it as text
EXPORT_MIME = {
	"application/vnd.google-apps.document" : "text/plain"
}

# Handle OAuth flow and return authenticated service
def authenticate():
	creds = None

	# Load existing token if exists
	if os.path.exists(TOKEN_FILE):
		creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

	# Otherwise run OAauth flow
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				CREDENTIALS_FILE, SCOPES
			)
			creds = flow.run_local_server(port=0)
		with open(TOKEN_FILE, "w") as token:
			token.write(creds.to_json())
	service = build("drive", "v3", credentials=creds)
	print("Google Drive authenticated successfully")
	return service

def fetch_drive_files(service, max_files=None):
    mime_query = " or ".join(
        [f"mimeType='{mime}'" for mime in SUPPORTED_MIME_TYPES.keys()]
    )

    query = (
        f"({mime_query}) "
        f"and trashed=false "
        f"and 'me' in owners"
    )

    files = []
    page_token = None

    while True:
        response = service.files().list(
            q=query,
            spaces="drive",
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, parents, size)",
            orderBy="modifiedTime desc",
            pageToken=page_token
        ).execute()

        batch = response.get("files", [])

        for f in batch:
            name = f.get("name", "").lower()
            mime_type = f.get("mimeType", "").lower()
            
            # 1. Skip explicit image or archive extensions
            if any(name.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                print(f"  [Skipped] Image/Archive extension blocked: {f['name']}")
                continue
                
            # 2. Skip anything Google Drive officially flags as an image MIME type
            if mime_type.startswith("image/"):
                print(f"  [Skipped] Image MIME type blocked: {f['name']}")
                continue

            # 3. Skip files matching training/dataset keywords
            if any(keyword in name for keyword in EXCLUDED_KEYWORDS):
                print(f"  [Skipped] Keyword match ('{name}'): {f['name']}")
                continue

            # 4. Skip binary files larger than 500 KB 
            # (Safe for Google Docs, which don't return a 'size' attribute)
            if "size" in f:
                size = int(f["size"])
                if size > 500000:
                    print(f"  [Skipped] File too large ({(size/1024):.1f} KB): {f['name']}")
                    continue

            files.append(f)

        page_token = response.get("nextPageToken")

        if not page_token:
            break

    print(f"\nFound {len(files)} valid files to process in Google Drive")
    return files


def build_gdrive_index():
    configure_embed_model()
    service = authenticate()
    files = fetch_drive_files(service)  # No cap argument needed anymore

    if not files:
        print("No supported files found in Google Drive.")
        return

    documents = []

    for file in files:
        print(f"  Processing: {file['name']}")
        content = download_file(service, file)

        if not content or not content.strip():
            continue

        doc = Document(
            text=content,
            metadata={
                "source": "google_drive",
                "file_name": file["name"],
                "file_id": file["id"],
                "mime_type": SUPPORTED_MIME_TYPES.get(file["mimeType"], "unknown"),
                "last_modified_date": file.get("modifiedTime", "unknown")[:10],
            }
        )
        documents.append(doc)

    print(f"\nIndexing {len(documents)} Drive documents...")

    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    storage_context = get_storage_context()

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True
    )

    print("Google Drive indexed successfully!")
    return index

def download_file(service, file):
    mime_type = file["mimeType"]
    file_id = file["id"]

    try:
        if mime_type in EXPORT_MIME:
            # FIX: Change fileID=file_id to fileId=file_id
            request = service.files().export_media(
                fileId=file_id,
                mimeType=EXPORT_MIME[mime_type]
            )
        else:
            request = service.files().get_media(fileId=file_id)
            
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"   Skipping {file['name']}: {e}")
        return None

def load_gdrive_index():
	"""Load existing index without re-fetching from Drive"""
	configure_embed_model()
	vector_store = get_vector_store()
	storage_context = get_storage_context()
	return VectorStoreIndex.from_vector_store(
		vector_store,
		storage_context=storage_context
	)