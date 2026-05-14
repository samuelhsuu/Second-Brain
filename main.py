from ingestion.obsidian_reader import build_obsidian_index
from ingestion.gdrive_reader import build_gdrive_index
from agent.brain import ask
import sys

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] == "index":
			# only index obsidian
			build_obsidian_index()
		elif sys.argv[1] == "index-drive":
			# only index g-drive
			build_gdrive_index()
		elif sys.argv[1] == "index-all":
			# index both
			build_obsidian_index()
			build_gdrive_index()
	else:
		print("Second Brain ready. Type 'exit' to quit.\n")
		while True:
			question = input("You: ").strip()
			if question.lower() == "exit":
				break
			if question:
				ask(question)