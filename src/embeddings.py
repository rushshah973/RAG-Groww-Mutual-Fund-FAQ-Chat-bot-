import requests
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
import config

class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Custom ChromaDB Embedding Function that calls the Google Gemini Developer API
    wire-free (using requests) to prevent importing PyTorch/Transformers locally,
    avoiding memory-limit crashes (OOM) on free hosts like Render.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment or config.")

    def __call__(self, input: Documents) -> Embeddings:
        # ChromaDB expects a list of embeddings (list of lists of floats) corresponding to each document input
        if not input:
            return []
            
        # The batchEmbedContents endpoint accepts up to 100 requests per call
        # We can chunk our list of inputs into batches of 50 to be safe
        embeddings = []
        batch_size = 50
        
        for i in range(0, len(input), batch_size):
            batch_texts = input[i:i+batch_size]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents?key={self.api_key}"
            
            payload = {
                "requests": [
                    {
                        "model": "models/gemini-embedding-001",
                        "content": {
                            "parts": [{"text": text}]
                        }
                    }
                    for text in batch_texts
                ]
            }
            
            import time
            max_retries = 5
            backoff = 2
            
            for attempt in range(max_retries):
                try:
                    headers = {"Content-Type": "application/json"}
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    
                    if response.status_code == 429:
                        print(f"Gemini API returned 429 (Rate Limit). Retrying in {backoff} seconds (Attempt {attempt+1}/{max_retries})...")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                        
                    if response.status_code != 200:
                        raise Exception(f"Gemini API returned status code {response.status_code}: {response.text}")
                    
                    res_data = response.json()
                    batch_embeddings = res_data.get("embeddings", [])
                    
                    for emb in batch_embeddings:
                        embeddings.append(emb["values"])
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Error fetching embeddings from Gemini: {e}")
                        raise e
                    time.sleep(backoff)
                    backoff *= 2
                
        return embeddings
