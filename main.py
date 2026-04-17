from ingestion.obsidian_reader import build_obsidian_index
from agent.brain import ask
import sys

if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == "index":
		build_obsidian_index()
	else:
		print("Second Brain ready. Type 'exit' to quit.\n")
		while True:
			question = input("You: ").strip()
			if question.lower() == "exit":
				break
			if question:
				ask(question)