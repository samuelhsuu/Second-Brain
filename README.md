# Second Brain Assistant

A personal assistant that lets you conversate with your own notes and documents using RAG (Retrieval-Augmented Generation).

## Tools

* Orchestration: LlamaIndex
* Vector store:  ChromaDB (local)
* Embeddings:    Ollama 'nomic-embed-text' (local) or OpenAI 'text-embedding-3-small'
* LLM:           Ollama 'llama3.2:1b' (local) or 'gpt-4o'
* Data Sources:  Obsidian, Google Drive

## Goals
* Establish Obsidian as a source ✓
* Establish Google Drive as a source
* Develop a UI

## UI

Run the local web UI from the project root:

```powershell
.\venv\Scripts\python.exe -m ui.app
```

Then open:

```text
http://127.0.0.1:7860
```

To stop:
Get-CimInstance Win32_Process -Filter "CommandLine LIKE '%ui.app%'" | Select-Object ProcessId, CommandLine
Stop-Process -Id 6480

## Current state
Obsidian notes can be indexed and cited by 
