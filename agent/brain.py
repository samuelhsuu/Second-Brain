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

    print(f"\nAnswer:\n{response}\n")

    print("\nSources:")
    print(f"{'─' * 72}")
    print(f"  {'File':<28} {'Course':<10} {'Semester':<13} {'Modified':<12} {'Score'}")
    print(f"{'─' * 72}")

    for node in response.source_nodes:
        meta = node.metadata
        file_name = meta.get("file_name", "unknown")
        course = meta.get("course", "unknown")
        semester = meta.get("semester", "unknown")
        modified = meta.get("last_modified_date", "unknown")
        score = node.score or 0.0

        # Truncate long values to keep table aligned
        if len(file_name) > 26:
            file_name = file_name[:23] + "..."
        if len(course) > 8:
            course = course[:8]
        if len(semester) > 11:
            semester = semester[:11]

        print(f"  {file_name:<28} {course:<10} {semester:<13} {modified:<12} {score:.2f}")

    print(f"{'─' * 72}\n")