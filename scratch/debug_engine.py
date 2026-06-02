import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import chromadb
from chromadb.utils import embedding_functions
import requests
import json
import re

import config
import llm_engine

def debug_rag():
    db_dir = config.VECTOR_STORE_DIR
    print(f"Chroma DB Path: {db_dir}")
    client = chromadb.PersistentClient(path=db_dir)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL_NAME)
    collection = client.get_collection(name=config.CHROMA_COLLECTION_NAME, embedding_function=emb_fn)
    
    query = "What schemes are in Axis Mutual Fund?"
    print(f"\nQuery: '{query}'")
    
    results = collection.query(
        query_texts=[query],
        where={"amc_name": "Axis Mutual Fund"},
        n_results=15
    )
    chunks = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    
    print("\n--- RETRIEVED CHUNKS ---")
    for idx, chunk in enumerate(chunks, 1):
        print(f"Chunk {idx}:")
        print(repr(chunk))
        print(f"Metadata: {metadatas[idx-1]}\n")
        
    # 2. Test fallback_extractor
    fallback_res = llm_engine.fallback_extractor(query, chunks, metadatas)
    print("--- FALLBACK EXTRACTOR OUTPUT ---")
    print(repr(fallback_res))
    
    # 3. Test API call
    gemini_key = config.GEMINI_API_KEY
    print(f"\nGemini Key Present: {'Yes' if gemini_key else 'No'}")
    
    context = "\n---\n".join(chunks)
    system_prompt = (
        "You are a facts-only Mutual Fund FAQ Assistant.\n"
        "Answer the user's query using ONLY the retrieved factual context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Query:\n{query}\n\n"
        "Constraints:\n"
        "1. Answer using ONLY the provided facts. Do not make assumptions or extrapolate.\n"
        "2. If the answer cannot be found in the context, respond exactly with: 'I cannot verify this information from the official sources.'\n"
        "3. Do not offer investment advice, comparisons, or performance opinions.\n"
        "4. Keep the response extremely brief. Do not exceed 3 sentences."
    )
    
    if gemini_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": system_prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 200
            }
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"\nGemini Response Code: {response.status_code}")
            if response.status_code == 200:
                print("Gemini Response Text:")
                print(repr(response.json()["candidates"][0]["content"]["parts"][0]["text"]))
            else:
                print("Gemini Error Text:")
                print(response.text)
        except Exception as e:
            print("Gemini Request Exception:", e)

if __name__ == "__main__":
    debug_rag()
