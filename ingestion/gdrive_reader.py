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

def fetch_drive_files(service):
	mime_query = " or ".join(
		[f"mimeType='{mime}'"for mime in SUPPORTED_MIME_TYPES.keys()]
	)
	query = f"({mime_query}) and trashed=false"

	files = []
	page_token = None

	while True:
		response = service.files().list(
			q=query,
			spaces="drive",
			fields="nextPageToken, files(id, name, mimeType, modifiedTime, parents)",
			pageToken=page_token
		).execute()

		files.extend(response.get("files", []))
		page_token = response.get("nextPageToken")

		if not page_token:
			break

	print(f"Found {len(files)} files in Google Drive")
	return files

def download_file(service, file):
	mime_type = file["mimeType"]
	file_id = file["id"]

	try:
		if mime_type in EXPORT_MIME:
			request = service.files().export_media(
				fileID=file_id,
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

def build_gdrive_index():
	configure_embed_model()
	service = authenticate()
	files = fetch_drive_files(service)

	documents = []
	for file in files:
		content = download_file(service, file)
		if not content or not content.strip():
			continue

		doc = Document(
			text=content,
			metadata={
				"source":"google_drive",
				"file_name":file["name"],
				"file_id": file["id"],
				"mime_type": SUPPORTED_MIME_TYPES.get(file["mimeType"], "unknown"),
				"last_modified_date":file.get("modifiedTime","unknown")[:10],
			}
		)
		documents.append(doc)

	splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
	storage_context = get_storage_context()

	index = VectorStoreIndex.from_documents(
		documents,
		storage_context=storage_context,
		transformations=[splitter],
		show_progress=True
	)
	return index

def load_gdrive_index():
	"""Load existing index without re-fetching from Drive"""
	configure_embed_model()
	vector_store = get_vector_store()
	storage_context = get_storage_context()
	return VectorStoreIndex.from_vector_store(
		vector_store,
		storage_context=storage_context
	)