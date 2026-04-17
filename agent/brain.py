from ingestion.obsidian_reader import load_obsidian_index
from pipeline.embedder import configure_embed_model
from pipeline.llm import configure_llm

# Configures both models and loads the index
def get_query_engine():
	configure_embed_model()
	configure_llm()

	index = load_obsidian_index()
	query_engine = index.as_query_engine(
		similarity_top_k = 5,
		response_mode = "compact"
	)
	return query_engine

# Runs the question asked through full RAG pipeline
def ask(question: str):
	engine = get_query_engine()
	response = engine.query(question)

	print(f"\nAnswer: \n{response}\n")
	print("Sources:")
	for node in response.source_nodes:
		meta = node.metadata
		print(f" Obsidian ({meta.get('vault', 'unknown')}) - "
			  f"{meta.get('file_name', 'unknown')} "
			  f"(score: {node.score:.2f})"
			)