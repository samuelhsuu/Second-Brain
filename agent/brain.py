from ingestion.obsidian_reader import load_obsidian_index
from ingestion.gdrive_reader import load_gdrive_index
from pipeline.embedder import configure_embed_model
from pipeline.llm import configure_llm
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core import PromptTemplate


def get_query_engine():
    configure_embed_model()
    configure_llm()

    obsidian_index = load_obsidian_index()
    gdrive_index = load_gdrive_index()

    # Create a retriever for gdrive and obsidian
    obsidian_retriever = VectorIndexRetriever(index=obsidian_index, similarity_top_k=10)
    gdrive_retriever = VectorIndexRetriever(index=gdrive_index, similarity_top_k=10)

    # Merge retrievers so queries search across both sources
    combined_retriever = QueryFusionRetriever(
        retrievers=[obsidian_retriever, gdrive_retriever],
        similarity_top_k=5,
        num_queries=1,  # 1 = no query rewriting
        use_async=False,
    )

    # Specify desired response
    qa_prompt = PromptTemplate(
    "You are a knowledgeable personal assistant with access to the user's notes and documents.\n"
    "Answer the question as thoroughly and helpfully as possible.\n"
    "Expand on concepts, provide context, and explain your reasoning.\n"
    "If the context contains relevant information, use it as your primary source but feel free\n"
    "to elaborate and connect ideas beyond what is literally written.\n"
    "If the context is insufficient, say so, but still share what you know.\n\n"
    "Context:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Question: {query_str}\n"
    "Answer thoroughly:\n"
    )


    query_engine = RetrieverQueryEngine.from_args(
        retriever=combined_retriever,
        response_mode=ResponseMode.TREE_SUMMARIZE,
        text_qa_template=qa_prompt,
    )
    return query_engine

def ask(question: str):
    engine = get_query_engine()
    response = engine.query(question)

    print(f"\nAnswer:\n{response}\n")

    print("\nSources:")
    print(f"{'─' * 80}")
    print(f"  {'File':<28} {'Source':<14} {'Course':<10} {'Semester':<13} {'Score'}")
    print(f"{'─' * 80}")

    for node in response.source_nodes:
        meta = node.metadata
        file_name = meta.get("file_name", "unknown")
        source = meta.get("source", "unknown")
        course = meta.get("course", "—")
        semester = meta.get("semester", "—")
        score = node.score or 0.0

        if len(file_name) > 26:
            file_name = file_name[:23] + "..."
        if len(course) > 8:
            course = course[:8]
        if len(semester) > 11:
            semester = semester[:11]

        print(f"  {file_name:<28} {source:<14} {course:<10} {semester:<13} {score:.2f}")

    print(f"{'─' * 80}\n")