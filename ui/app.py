import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

import streamlit as st
import pandas as pd
from agent.brain import get_query_engine, query_with_sources

st.set_page_config(page_title="Second Brain", layout="wide")
st.title("Second Brain")

# Cache query engine so ChromaDB is only loaded once per session
@st.cache_resource
def load_engine():
	return get_query_engine()

engine = load_engine()

# Sidebar
with st.sidebar:
	st.header("Controls")
	source_filter = st.radio(
		"Source filter",
		options = ["All", "Obsidian", "Google Drive"],
		index = 0
	)
	st.divider()
	if st.button("Reindex everything"):
		with st.spinner("Reindexing..."):
			from ingestion.obsidian_reader import build_obsidian_index
			from ingestion.gdrive_reader import build_gdrive_index
			build_obsidian_index()
			build_gdrive_index()
			load_engine.clear() # clear cache
		st.success("Reindexing complete!")

# initialize message history
if "messages" not in st.session_state:
	st.session_state.messages = []
for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		st.write(message["content"])
		if message["role"] == "assistant" and message.get("sources"):
			with st.expander("Sources"):
				st.dataframe(pd.DataFrame(message["sources"]), hide_index = True)

# chat input
question = st.chat_input("Ask your Second Brain...")
if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # run query first to get full response
            answer, sources = query_with_sources(question, engine)
            
            if source_filter == "Obsidian":
                sources = [s for s in sources if s["source"] == "obsidian"]
            elif source_filter == "Google Drive":
                sources = [s for s in sources if s["source"] == "google_drive"]

        # stream answer word by word after query completes
        def word_generator():
            for word in answer.split(" "):
                yield word + " "
                time.sleep(0.04)

        st.write_stream(word_generator())

        with st.expander("Sources"):
            st.dataframe(pd.DataFrame(sources), hide_index=True)

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})