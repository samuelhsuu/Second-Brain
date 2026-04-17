from dotenv import load_dotenv
from config import OBSIDIAN_VAULT_PATH
import os

load_dotenv(override=True)

raw = os.getenv("OBSIDIAN_VAULT_PATH", "")
print("Raw value:", repr(raw))

stripped = raw.strip('"').strip("'")
print("Stripped value:", repr(stripped))

print("Exists:", os.path.exists(stripped))
print("Config sees:", repr(OBSIDIAN_VAULT_PATH))
