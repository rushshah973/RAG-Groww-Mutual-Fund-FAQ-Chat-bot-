import os

def load_env():
    """
    Loads environment variables from a local .env file if it exists.
    """
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    # Strip quotes if present
                    val = val.strip().strip("'\"")
                    os.environ[key.strip()] = val

# Auto-load on import
load_env()

# Application configuration parameters with fallback defaults
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

RAW_DOCUMENTS_DIR = os.environ.get("RAW_DOCUMENTS_DIR", "data/raw_documents")
VECTOR_STORE_DIR = os.environ.get("VECTOR_STORE_DIR", "data/vector_store")
CHUNKS_JSON_PATH = os.environ.get("CHUNKS_JSON_PATH", "data/chunks.json")

EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
CHROMA_COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION_NAME", "mutual_fund_facts")

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "64"))

SCHEDULER_HOUR = int(os.environ.get("SCHEDULER_HOUR", "9"))
SCHEDULER_MINUTE = int(os.environ.get("SCHEDULER_MINUTE", "25"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
