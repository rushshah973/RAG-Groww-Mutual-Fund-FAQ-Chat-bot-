import os
import chromadb
from chromadb.utils import embedding_functions
import config
import llm_engine

def test_full_rag():
    db_dir = config.VECTOR_STORE_DIR
    if not os.path.exists(db_dir):
        print(f"Error: Vector store directory '{db_dir}' does not exist.")
        return
        
    print("Initializing ChromaDB persistent client...")
    client = chromadb.PersistentClient(path=db_dir)
    
    print(f"Loading SentenceTransformer embedding function (model: {config.EMBEDDING_MODEL_NAME})...")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL_NAME)
    
    try:
        collection = client.get_collection(name=config.CHROMA_COLLECTION_NAME, embedding_function=emb_fn)
    except Exception as e:
        print(f"Error retrieving collection: {e}")
        return
        
    test_queries = [
        "What is the exit load of SBI Small Cap Fund?",
        "Who is the fund manager of ICICI Prudential Bluechip Fund?",
        "How do I request an account statement from HDFC Mutual Fund?",
        "What is the exit load of Axis Small Cap Fund?",
        "Who is the fund manager of Axis Small Cap Fund?",
        "What is the exit load of Groww Gold ETF FOF?",
        "Who is the fund manager of Tata Small Cap Fund?",
        "What is the benchmark index of ICICI Prudential Multi-Asset Fund?"
    ]
    
    # Verify API key loaded
    print(f"Gemini API key configured: {'Yes' if config.GEMINI_API_KEY else 'No'}")
    print(f"OpenAI API key configured: {'Yes' if config.OPENAI_API_KEY else 'No'}")
    
    for i, query in enumerate(test_queries, 1):
        print("\n" + "="*80)
        print(f"Query {i}: '{query}'")
        print("="*80)
        
        # 1. Retrieve context
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        chunks = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        if not chunks:
            print("No matching context retrieved from database.")
            continue
            
        print(f"Retrieved {len(chunks)} relevant chunks from ChromaDB.")
        
        # 2. Generate answer
        print("Generating answer using LLM Engine...")
        res = llm_engine.generate_answer(query, chunks, metadatas)
        
        print("\nFinal Output Answer:")
        print(res["answer"])
        print(f"Source URL: {res['source_url']}")
        print(f"Last Updated: {res['last_updated']}")
        print("-" * 80)

if __name__ == "__main__":
    test_full_rag()
