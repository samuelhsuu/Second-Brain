# Second Brain Assistant

A personal assistant that lets you conversate with your own notes and documents using RAG (Retrieval-Augmented Generation).

https://github.com/user-attachments/assets/8b034af9-d177-4810-8118-a76b79511649

## Tools

* Orchestration: LlamaIndex
* Vector store:  ChromaDB (local)
* Embeddings:    Ollama 'nomic-embed-text' (local) or OpenAI 'text-embedding-3-small'
* LLM:           Ollama 'llama3.2:1b' (local) or 'gpt-4o'
* Data Sources:  Obsidian, Google Drive

## Goals
* Establish Obsidian as a source ✓
* Establish Google Drive as a source ✓
* Develop a UI ✓

## Current state
A UI is available to interact with the model. It also supports reindexing notes, sorting by sources, and a source dropdown table