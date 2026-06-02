import os
import chromadb
from chromadb.utils import embedding_functions
import config

def test_retrieval():
    db_dir = config.VECTOR_STORE_DIR
    if not os.path.exists(db_dir):
        print(f"Error: Vector store directory '{db_dir}' does not exist. Please run index_builder.py first.")
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
        "How do I download the HDFC account statement?",
        "What is the exit load of SBI Small Cap Fund?",
        "Who is the fund manager of ICICI Prudential Bluechip Fund?",
        "What is the expense ratio of UTI Long Term Equity Fund?",
        "Is there an ELSS lock-in period for Kotak Mahindra?",
        "What is the expense ratio of Axis Small Cap Fund?",
        "Who is the fund manager of Axis Small Cap Fund?",
        "What is the exit load of ICICI Prudential Multi-Asset Fund?",
        "What is the expense ratio of UTI Small Cap Fund?",
        "What is the lock-in period for Groww Silver ETF FoF?",
        "Who is the fund manager of Nippon India Large Cap Fund?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print("\n" + "="*80)
        print(f"Query {i}: '{query}'")
        print("="*80)
        
        results = collection.query(
            query_texts=[query],
            n_results=5
        )
        
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        if not documents:
            print("No matches found.")
            continue
            
        for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            print(f"\nMatch {idx+1} (Distance/Score: {dist:.4f}):")
            print(f"Content: {doc}")
            print(f"Metadata:")
            print(f"  - AMC: {meta.get('amc_name')}")
            print(f"  - Scheme: {meta.get('scheme_name')}")
            print(f"  - Type: {meta.get('document_type')}")
            print(f"  - Source URL: {meta.get('source_url')}")
            print(f"  - Extracted Date: {meta.get('extracted_date')}")

if __name__ == "__main__":
    test_retrieval()
