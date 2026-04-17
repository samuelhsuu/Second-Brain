from config import USE_LOCAL_MODELS, LLM_MODEL
from llama_index.core import Settings


def configure_llm():
    if USE_LOCAL_MODELS:
        from llama_index.llms.ollama import Ollama

        Settings.llm = Ollama(model=LLM_MODEL, request_timeout=120)
        print(f"Using local LLM: {LLM_MODEL}")
    else:
        from llama_index.llms.openai import OpenAI
        import openai
        from config import OPENAI_API_KEY

        openai.api_key = OPENAI_API_KEY
        Settings.llm = OpenAI(model=LLM_MODEL)
        print(f"Using local LLM: {LLM_MODEL}")
