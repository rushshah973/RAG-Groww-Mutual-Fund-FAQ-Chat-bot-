import sys
import os
import json
import re
import chromadb
from chromadb.utils import embedding_functions

sys.path.insert(0, "/Users/rushabh/Mutual Fund Milestone/src")
import config
import llm_engine

# Initialize ChromaDB
db_dir = config.VECTOR_STORE_DIR
client = chromadb.PersistentClient(path=db_dir)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL_NAME)
collection = client.get_or_create_collection(name=config.CHROMA_COLLECTION_NAME, embedding_function=emb_fn)

test_queries = [
    "What is the minimum SIP amount for HDFC Index Fund?",
    "What schemes are in HDFC Mutual Fund?"
]

for q in test_queries:
    print("\n" + "="*80)
    print(f"TRACING QUERY: {q}")
    print("="*80)
    
    # Retrieve from DB
    results = collection.query(query_texts=[q], n_results=5)
    chunks = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    
    print(f"Retrieved {len(chunks)} chunks:")
    for idx, (c, m) in enumerate(zip(chunks, metadatas)):
        print(f"  [{idx}] Scheme: {m.get('scheme_name')} | AMC: {m.get('amc_name')} | DocType: {m.get('document_type')}")
        print(f"      Text snippet: {c[:120]}...")
        
    # Trace subject words
    query_lower = q.lower()
    stop_words = {
        "what", "is", "the", "of", "for", "in", "and", "to", "a", "an", "who", "will", 
        "win", "how", "much", "amount", "period", "index", "details", "contact", 
        "support", "email", "phone", "download", "request", "statement", "report", 
        "process", "exit", "load", "expense", "ratio", "minimum", "sip", "lock-in", 
        "lock", "riskometer", "classification", "benchmark", "manager", "managers", 
        "credentials", "experience", "tenure", "managing", "since", "value", "type", 
        "direct", "regular", "plan", "plans", "fund", "funds", "mutual", "assistant",
        "please", "ask", "related", "made", "query", "queries", "give", "tell", "show", "get"
    }
    query_words = set(re.findall(r'\b[a-z]{3,}\b', query_lower))
    subject_words = query_words - stop_words
    print(f"Query Words: {query_words}")
    print(f"Subject Words (Required to match): {subject_words}")
    
    # Trace filtering
    filtered_chunks = []
    mentioned_amcs = ["hdfc"]  # force hdfc for trace
    
    for chunk, meta in zip(chunks, metadatas):
        amc_name = meta.get("amc_name", "").lower()
        scheme_name = meta.get("scheme_name", "").lower()
        
        # Scheme mismatch check
        scheme_keywords = ["bluechip", "small cap", "small", "cap", "long term", "tax saver", "taxsaver", "flexicap", "flexi cap", "emerging", "mid-cap", "mid cap", "opportunities", "value", "discovery", "digital", "total market", "index"]
        mismatch = False
        mismatch_reason = ""
        if scheme_name != "general":
            for kw in scheme_keywords:
                if kw in query_lower:
                    if kw not in scheme_name:
                        mismatch = True
                        mismatch_reason = f"Keyword '{kw}' in query but not in scheme name '{scheme_name}'"
                        break
                        
        # Subject words match check
        chunk_lower = chunk.lower()
        meta_values_lower = " ".join([str(v).lower() for v in meta.values()])
        unmatched_words = []
        for word in subject_words:
            if word not in chunk_lower and word not in meta_values_lower:
                unmatched_words.append(word)
                
        print(f"-> Chunk scheme: {scheme_name}")
        if mismatch:
            print(f"   REJECTED: Scheme keyword mismatch: {mismatch_reason}")
        elif unmatched_words:
            print(f"   REJECTED: Unmatched subject words: {unmatched_words}")
        else:
            print(f"   ACCEPTED!")
            filtered_chunks.append(chunk)
            
    print(f"Filtered chunks remaining: {len(filtered_chunks)}")
    
    # Run through full generate_answer
    ans = llm_engine.generate_answer(q, chunks, metadatas)
    print(f"FINAL ANSWER: {ans['answer']}")
