import os
import json
import chromadb
from embeddings import GeminiEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config

def load_documents_and_build_index():
    raw_dir = config.RAW_DOCUMENTS_DIR
    db_dir = config.VECTOR_STORE_DIR
    
    if not os.path.exists(raw_dir):
        print(f"Error: Raw documents directory '{raw_dir}' does not exist.")
        return
        
    os.makedirs(db_dir, exist_ok=True)
    
    # 1. Initialize ChromaDB client and collection
    print("Initializing ChromaDB persistent client...")
    client = chromadb.PersistentClient(path=db_dir)
    
    print("Setting up Gemini API-based embedding function...")
    emb_fn = GeminiEmbeddingFunction(api_key=config.GEMINI_API_KEY)
    
    # Delete existing collection if we want a fresh index
    try:
        client.delete_collection(config.CHROMA_COLLECTION_NAME)
        print(f"Deleted existing '{config.CHROMA_COLLECTION_NAME}' collection.")
    except Exception:
        pass
        
    collection = client.create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        embedding_function=emb_fn
    )
    
    # 2. Text Splitter configuration (Phase 2 subpart 2)
    # Target chunk_size = 512 characters, chunk_overlap = 64 characters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    
    documents_to_add = []
    metadatas_to_add = []
    ids_to_add = []
    id_counter = 0
    
    # 3. Read and parse JSON files (Phase 2 subpart 1)
    for filename in os.listdir(raw_dir):
        if not filename.endswith(".json"):
            continue
            
        file_path = os.path.join(raw_dir, filename)
        print(f"Processing structured document: {filename}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
            
        source_url = doc_data.get("url", "")
        extracted_date = doc_data.get("extracted_date", "2026-05-31")
        amc_name = doc_data.get("scheme_name", "Unknown Mutual Fund")
        
        structured = doc_data.get("structured_data", {})
        if not structured:
            print(f"Warning: No 'structured_data' found in {filename}")
            continue
            
        # Parse About section
        about_text = structured.get("about", "")
        if about_text:
            text = f"About {amc_name}: {about_text}"
            meta = {
                "amc_name": amc_name,
                "scheme_name": "General",
                "document_type": "amc_profile",
                "source_url": source_url,
                "extracted_date": extracted_date
            }
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                documents_to_add.append(chunk)
                metadatas_to_add.append(meta)
                ids_to_add.append(f"doc_{id_counter}")
                id_counter += 1
                
        # Parse Support Contact section
        support = structured.get("support_contact", {})
        if support:
            email = support.get("email", "")
            phone = support.get("phone", "")
            text = f"Customer Support contact details for {amc_name}: Email: {email}, Phone: {phone}."
            meta = {
                "amc_name": amc_name,
                "scheme_name": "General",
                "document_type": "amc_profile",
                "source_url": source_url,
                "extracted_date": extracted_date
            }
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                documents_to_add.append(chunk)
                metadatas_to_add.append(meta)
                ids_to_add.append(f"doc_{id_counter}")
                id_counter += 1
                
        # Parse Servicing Processes section
        processes = structured.get("servicing_processes", {})
        if processes:
            # Account Statement
            stmt = processes.get("account_statement", "")
            if stmt:
                text = f"Process to download or request Account Statement from {amc_name}: {stmt}"
                meta = {
                    "amc_name": amc_name,
                    "scheme_name": "General",
                    "document_type": "servicing_process",
                    "source_url": source_url,
                    "extracted_date": extracted_date
                }
                chunks = text_splitter.split_text(text)
                for chunk in chunks:
                    documents_to_add.append(chunk)
                    metadatas_to_add.append(meta)
                    ids_to_add.append(f"doc_{id_counter}")
                    id_counter += 1
                    
            # Capital Gains Report
            cg = processes.get("capital_gains_report", "")
            if cg:
                text = f"Process to download or request Capital Gains Report/Statement from {amc_name}: {cg}"
                meta = {
                    "amc_name": amc_name,
                    "scheme_name": "General",
                    "document_type": "servicing_process",
                    "source_url": source_url,
                    "extracted_date": extracted_date
                }
                chunks = text_splitter.split_text(text)
                for chunk in chunks:
                    documents_to_add.append(chunk)
                    metadatas_to_add.append(meta)
                    ids_to_add.append(f"doc_{id_counter}")
                    id_counter += 1
                    
            # Tax Savings Section 80C
            tax = processes.get("tax_savings_80c", "")
            if tax:
                text = f"Tax Savings (Section 80C) benefits and ELSS lock-in guidelines for {amc_name}: {tax}"
                meta = {
                    "amc_name": amc_name,
                    "scheme_name": "General",
                    "document_type": "servicing_process",
                    "source_url": source_url,
                    "extracted_date": extracted_date
                }
                chunks = text_splitter.split_text(text)
                for chunk in chunks:
                    documents_to_add.append(chunk)
                    metadatas_to_add.append(meta)
                    ids_to_add.append(f"doc_{id_counter}")
                    id_counter += 1
                    
        # Parse Schemes section
        schemes = structured.get("schemes", [])
        for scheme in schemes:
            scheme_name = scheme.get("name", "Unknown Scheme")
            scheme_type = scheme.get("type", "Unknown Type")
            
            exp_ratio = scheme.get("expense_ratio", {})
            direct_exp = exp_ratio.get("direct", "N/A")
            reg_exp = exp_ratio.get("regular", "N/A")
            
            exit_load = scheme.get("exit_load", "N/A")
            min_sip = scheme.get("minimum_sip", "N/A")
            lock_in = scheme.get("lock_in_period", "N/A")
            riskometer = scheme.get("riskometer", "N/A")
            benchmark = scheme.get("benchmark", "N/A")
            
            managers = scheme.get("fund_managers", [])
            mgr_desc_list = []
            for mgr in managers:
                name = mgr.get("name", "N/A")
                exp = mgr.get("experience", "N/A")
                cred = mgr.get("credentials", "N/A")
                tenure = mgr.get("tenure", "N/A")
                mgr_desc_list.append(f"{name} (Credentials: {cred}, Experience: {exp}, Tenure: {tenure})")
            managers_desc = "; ".join(mgr_desc_list)
            
            # Construct a comprehensive, descriptive paragraph for the scheme
            text = (
                f"Scheme factsheet details for '{scheme_name}' managed by {amc_name}. "
                f"Type: {scheme_type}. "
                f"Expense Ratio: Direct Plan is {direct_exp}, Regular Plan is {reg_exp}. "
                f"Exit Load: {exit_load} "
                f"Minimum SIP Amount: {min_sip}. "
                f"Lock-in Period: {lock_in}. "
                f"Riskometer Classification: {riskometer}. "
                f"Benchmark Index: {benchmark}. "
                f"Fund Managers: {managers_desc}."
            )
            
            meta = {
                "amc_name": amc_name,
                "scheme_name": scheme_name,
                "document_type": "scheme_factsheet",
                "source_url": source_url,
                "extracted_date": extracted_date
            }
            
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                documents_to_add.append(chunk)
                metadatas_to_add.append(meta)
                ids_to_add.append(f"doc_{id_counter}")
                id_counter += 1
                
    # 4. Save chunks to a human-readable chunks.json file
    chunks_list = []
    for doc, meta, doc_id in zip(documents_to_add, metadatas_to_add, ids_to_add):
        chunks_list.append({
            "id": doc_id,
            "text": doc,
            "metadata": meta
        })
    chunks_file_path = config.CHUNKS_JSON_PATH
    try:
        with open(chunks_file_path, "w", encoding="utf-8") as f:
            json.dump(chunks_list, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved all chunks to human-readable JSON: {chunks_file_path}")
    except Exception as e:
        print(f"Error saving chunks.json: {e}")

    # 5. Insert documents into ChromaDB in batches
    total_docs = len(documents_to_add)
    print(f"Total compiled chunks to index: {total_docs}")
    
    if total_docs == 0:
        print("No documents to index.")
        return
        
    batch_size = 50
    for i in range(0, total_docs, batch_size):
        end = min(i + batch_size, total_docs)
        collection.add(
            documents=documents_to_add[i:end],
            metadatas=metadatas_to_add[i:end],
            ids=ids_to_add[i:end]
        )
        print(f"Indexed batch {i // batch_size + 1}: Chunks {i} to {end-1}")
        
    print("Database build complete! All chunks successfully indexed in ChromaDB.")

if __name__ == "__main__":
    load_documents_and_build_index()
