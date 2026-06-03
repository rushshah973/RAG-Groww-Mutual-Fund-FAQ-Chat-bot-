import os
import sys
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Load sibling modules locally (Python adds the current executing directory to sys.path)
import config
import guardrails
import llm_engine
import scheduler

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mutual Fund FAQ Assistant",
    description="Facts-only mutual fund Q&A assistant with strict compliance guardrails.",
    version="1.0.0"
)

# Enable CORS for cross-origin requests (e.g. from Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    query: str

# Initialize ChromaDB client and collection using configs
db_dir = config.VECTOR_STORE_DIR
client = chromadb.PersistentClient(path=db_dir)

from embeddings import GeminiEmbeddingFunction
emb_fn = GeminiEmbeddingFunction(api_key=config.GEMINI_API_KEY)
collection = client.get_or_create_collection(name=config.CHROMA_COLLECTION_NAME, embedding_function=emb_fn)

@app.on_event("startup")
def startup_event():
    """
    Initializes background threads, including the database update scheduler.
    """
    print("Starting Mutual Fund FAQ Assistant Backend...")
    # Trigger non-blocking database scheduler daemon
    scheduler.start_scheduler()

@app.post("/api/query")
def query_endpoint(req: QueryRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    # 1. Run Guardrails Engine (PII & Advisory checking)
    guard_res = guardrails.validate_query(query)
    if guard_res["status"] == "violated":
        return {
            "status": guard_res["status"],
            "type": guard_res["type"],
            "answer": guard_res["message"],
            "source_url": "https://investor.sebi.gov.in/" if guard_res["type"] == "advisory" else None,
            "last_updated": None
        }
        
    # 2. Retrieve Context from ChromaDB
    try:
        # Detect if this is an AMC schemes list query
        query_lower = query.lower()
        is_list_query = False
        list_keywords = ["scheme", "schemes", "list", "fund", "funds", "portfolio", "offer"]
        if any(lk in query_lower for lk in list_keywords):
            specific_keywords = [
                "bluechip", "small cap", "small", "cap", "long term", "tax saver", "taxsaver",
                "flexicap", "flexi cap", "emerging", "mid-cap", "mid cap", "opportunities",
                "value", "discovery", "digital", "total market", "index", "contra",
                "multi asset", "multi-asset", "gold", "silver", "statement", "report",
                "download", "request", "contact", "support", "email", "phone", "exit",
                "load", "expense", "ratio", "minimum", "sip", "lock-in", "lock",
                "riskometer", "benchmark", "manager", "managers", "manager's"
            ]
            if not any(sk in query_lower for sk in specific_keywords):
                is_list_query = True

        matched_amc = None
        if is_list_query:
            amc_mapping = {
                "SBI Mutual Fund": ["sbi"],
                "HDFC Mutual Fund": ["hdfc"],
                "ICICI Prudential Mutual Fund": ["icici", "prudential"],
                "Kotak Mahindra Mutual Fund": ["kotak", "mahindra"],
                "Axis Mutual Fund": ["axis"],
                "Mirae Asset Mutual Fund": ["mirae", "asset"],
                "Nippon India Mutual Fund": ["nippon", "nippon india"],
                "Tata Mutual Fund": ["tata"],
                "UTI Mutual Fund": ["uti"],
                "Groww Mutual Fund": ["groww"]
            }
            for amc_name, keywords in amc_mapping.items():
                if any(kw in query_lower for kw in keywords):
                    matched_amc = amc_name
                    break

        if matched_amc:
            results = collection.query(
                query_texts=[query],
                where={"amc_name": matched_amc},
                n_results=15
            )
        else:
            results = collection.query(
                query_texts=[query],
                n_results=5
            )
            
        chunks = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
    except Exception as e:
        import traceback
        print(f"Error querying ChromaDB: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "type": "system",
            "answer": f"The system is temporarily unable to retrieve data. Error: {str(e)}",
            "source_url": None,
            "last_updated": None
        }
        
    # 3. Generate context-bound response
    try:
        gen_res = llm_engine.generate_answer(query, chunks, metadatas)
        return {
            "status": "success",
            "type": None,
            "answer": gen_res["answer"],
            "source_url": gen_res["source_url"],
            "last_updated": gen_res["last_updated"]
        }
    except Exception as e:
        print(f"Error generating answer: {e}")
        return {
            "status": "error",
            "type": "system",
            "answer": "An error occurred while compiling your response. Please try again.",
            "source_url": None,
            "last_updated": None
        }

@app.get("/api/metadata")
def get_metadata():
    """
    Returns unique lists of active AMCs and schemes for UI listing.
    """
    raw_dir = config.RAW_DOCUMENTS_DIR
    if not os.path.exists(raw_dir):
        return {"amcs": [], "schemes": []}
        
    amcs = []
    schemes = []
    
    import json
    for filename in os.listdir(raw_dir):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(raw_dir, filename), "r", encoding="utf-8") as f:
                    doc = json.load(f)
                    amc_name = doc.get("scheme_name", "")
                    if amc_name:
                        amcs.append(amc_name)
                    structured = doc.get("structured_data", {})
                    for s in structured.get("schemes", []):
                        s_name = s.get("name", "")
                        if s_name:
                            schemes.append({"name": s_name, "amc": amc_name})
            except Exception as e:
                print(f"Error reading metadata from {filename}: {e}")
                
    return {
        "amcs": sorted(list(set(amcs))),
        "schemes": sorted(schemes, key=lambda x: x["name"])
    }

# Mount static frontend interface files
os.makedirs("frontend", exist_ok=True)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    # Start backend server
    print(f"Launching FastAPI Server on {config.HOST}:{config.PORT}...")
    # Add the current directory (src/) to the uvicorn system path for auto-reload to resolve modules correctly
    sys.path.insert(0, os.path.dirname(__file__))
    uvicorn.run("app:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
