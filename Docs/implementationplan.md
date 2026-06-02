# Implementation Plan: Mutual Fund FAQ Assistant (Facts-Only Q&A)

This document maps out the phase-wise execution plan for building the RAG-based, compliance-guarded Mutual Fund FAQ Assistant.

---

## Phase 1: Project Setup & Corpus Collection [COMPLETED]
**Goal**: Establish the development workspace, configure dependencies, and compile a clean, structured corpus of official mutual fund scheme parameters.

### Accomplishments
1. **Workspace and Environment Configuration**:
   - Set up the project directory structure with designated folders for code logic (`src/`), structured documentation (`Docs/`), raw structured data (`data/raw_documents/`), and the client interface (`frontend/`).
   - Configured the Python virtual environment (`.venv`) and installed project dependencies in [requirements.txt](file:///Users/rushabh/Mutual%20Fund%20Milestone/Docs/requirements.txt) including `fastapi`, `uvicorn`, `chromadb`, `langchain-text-splitters`, `beautifulsoup4`, `requests`, `pydantic`, and `sentence-transformers`.
2. **Groww AMC Index Compilation**:
   - Created [groww_amcs.json](file:///Users/rushabh/Mutual%20Fund%20Milestone/groww_amcs.json) mapping 10 prominent AMCs (SBI, HDFC, ICICI Prudential, Kotak Mahindra, Axis, UTI, Mirae Asset, Nippon India, Tata, and Groww) to their official Groww endpoints.
3. **Structured Ingestion & Parser Pipeline**:
   - Implemented [ingest.py](file:///Users/rushabh/Mutual%20Fund%20Milestone/src/ingest.py) to parse Groww pages and clean boilerplate text (script, style, meta, header, footer, nav elements, and brief navigation links under 30 characters).
   - Created 10 structured, high-fidelity facts-only profile JSON files under [data/raw_documents/](file:///Users/rushabh/Mutual%20Fund%20Milestone/data/raw_documents/) containing official contact details (phone, email), servicing processes (account statements, capital gains reports, Section 80C ELSS details), and detailed parameters of core schemes (expense ratios, exit loads, minimum SIPs, lock-in periods, riskometer classifications, benchmark indexes, and fund manager experiences/tenures).

---

## Phase 2: RAG Pipeline & Embedding Construction
**Goal**: Process the structured JSON files, chunk content into logical, context-preserving text snippets, generate semantic embeddings, and build the persistent search index.

### Execution Steps
1. **Context-Preserving Text Construction**:
   - Write a parsing script `src/index_builder.py` that reads the 10 AMC JSON profiles from `data/raw_documents/`.
   - Convert structured keys (such as scheme factsheets, expense ratios, and servicing procedures) into descriptive, self-contained factual paragraphs. For example, convert:
     ```json
     { "name": "SBI Bluechip Fund", "exit_load": "1.00% if redeemed within 1 year..." }
     ```
     into:
     *"For SBI Mutual Fund's SBI Bluechip Fund (Large Cap style), the exit load is 1.00% if redeemed within 1 year (365 days) from allotment, and Nil after 1 year. The benchmark index is S&P BSE 100 TRI."*
     This ensures that retrieval context remains highly dense and coherent, avoiding broken semantic chunks.
2. **Text Chunking**:
   - Utilize `RecursiveCharacterTextSplitter` from `langchain-text-splitters`.
   - Set splitting thresholds to `chunk_size = 512` characters with `chunk_overlap = 64` characters. This range ensures that specific numbers (e.g. ratios, time limits) and support details are fully enclosed in singular queryable chunks.
3. **Vector Database Setup**:
   - Initialize a persistent local instance of `ChromaDB` inside the project at `data/vector_store/`.
   - Instantiate the `SentenceTransformer` model using `BAAI/bge-small-en-v1.5` to generate 384-dimensional dense semantic embeddings (offering high factual retrieval accuracy).
   - Insert document chunks alongside comprehensive metadata:
     - `amc_name`: Name of the fund house.
     - `scheme_name`: Specific scheme name, or `"General"` for AMC-wide procedures.
     - `document_type`: Tagged as `"amc_profile"`, `"scheme_factsheet"`, or `"servicing_process"`.
     - `source_url`: The official reference link (e.g. the Groww AMC or official scheme URL).
     - `extracted_date`: Timestamp representing data extraction to support verification.
4. **Retrieval Verification**:
   - Write a test runner script `src/retrieve_test.py` that performs sample semantic lookups (e.g., *"How to download Axis capital gains report?", "What is the exit load of Mirae Asset Large Cap?"*).
   - Log the retrieved chunks, metadata properties, and similarity scores to confirm indexing precision.

---

## Phase 3: Guardrail Engine (PII & Advisory Checks)
**Goal**: Intercept and deflect advisory queries, non-factual topics, or sensitive PII prior to calling the LLM.

### Execution Steps
1. **Advisory Query Classifier**:
   - Create a classification module in `src/guardrails.py` using rules, regular expressions, and semantic triggers.
   - Flag subjective advisory keywords (such as *"should I buy"*, *"which is better"*, *"recommend"*, *"best fund"*, *"comparison of returns"*).
   - If the input query is classified as Advisory, bypass the RAG/LLM engine and immediately return a standard compliance refusal:
     *"I can only provide objective, facts-only information about mutual fund schemes. I cannot provide investment advice, comparisons, or recommendations. For educational resources on mutual funds, please visit the [AMFI Investor Corner](https://www.amfiindia.com/investor-corner/knowledge-center/tax-benefits.html) or [SEBI Investor Education](https://investor.sebi.gov.in/)."*
2. **PII Scanner**:
   - Implement regex scanners inside `src/guardrails.py` to identify:
     - **Aadhaar Numbers**: `\b[2-9]\d{3}\s\d{4}\s\d{4}\b` and `\b[2-9]\d{11}\b` (with and without space separators).
     - **PAN Cards**: `\b[A-Z]{5}[0-9]{4}[A-Z]\b` (standard 10-character Indian Permanent Account Number format).
     - **Common Folio / OTP patterns**: Numeric strings explicitly preceding or succeeding terms like `"OTP"`, `"folio"`, `"account"`, or `"bank account"`.
   - If PII matches, halt execution immediately and return a privacy deflection:
     *"For security and privacy reasons, please do not share personally identifiable information (PII) such as PAN, Aadhaar, folio numbers, bank details, or OTPs. Transaction aborted."*

---

## Phase 4: LLM Generation & Output Constraints
**Goal**: Set up strict context-bound generation prompts and post-processing filters to enforce facts-only formatting.

### Execution Steps
1. **Context-Constrained Prompt Engineering**:
   - Implement a model caller module `src/llm_engine.py` that wraps LLM interactions.
   - Use a highly restrictive prompt template:
     ```text
     You are a facts-only Mutual Fund FAQ Assistant.
     Answer the user's query using ONLY the retrieved factual context below.
     
     Context:
     {context}
     
     Query:
     {query}
     
     Constraints:
     1. Answer using ONLY the provided facts.
     2. If the answer cannot be found in the context, respond exactly with: "I cannot verify this information from the official sources." Do not speculate, extrapolate, or suggest.
     3. Do not offer investment advice, comparisons, or performance opinions.
     4. Keep the response extremely brief. Do not exceed 3 sentences.
     ```
2. **Post-Processing & Output Validation**:
   - Capture the raw output from the generation model.
   - Run a clean sentence-splitter (e.g., regex boundary splitters `[.!?]`) and truncate the output to a maximum of 3 sentences.
   - Extract the `source_url` and `extracted_date` from the retrieved database metadata.
   - Format and append exactly one official link and the data recency footer:
     `Source: <source_url>`
     `Last updated from sources: <extracted_date>`

---

## Phase 5: UI & API Integration
**Goal**: Build a FastAPI web service backend and code a stunning, modern glassmorphic chat frontend.

### Execution Steps
1. **FastAPI Application (`src/app.py`)**:
   - Expose the main endpoint `POST /api/query` accepting `{ "query": "..." }`.
   - Expose `GET /api/metadata` returning the lists of indexed AMCs and their respective schemes.
   - Integrate static file hosting to serve the frontend files.
   - **Orchestration Flow**:
     - Receive query -> Run `src/guardrails.py` checks -> If failed, return refusal -> Retrieve top-K context from `ChromaDB` -> Generate answer via `src/llm_engine.py` -> Post-process response -> Send response payload.
2. **Premium Chat Interface (`frontend/`)**:
   - Structure static files: `index.html` (layout), `index.css` (modern styles), and `app.js` (logic).
   - **Design Guidelines**:
     - Implement a dark-themed glassmorphism layout with smooth gradient backgrounds (deep violet/blue to dark charcoal), semi-transparent container cards with frosted borders (`backdrop-filter: blur()`).
     - Load premium typography from Google Fonts (e.g., Outfit or Inter).
     - Add micro-animations (transitions on input focus, message loading indicators, and hover effects).
   - **Interface Components**:
     - Global, visible banner: `"Facts-only. No investment advice."`
     - Clean, scrollable chat panel showing user messages and assistant responses.
     - Clickable starter question cards (e.g., *"What is the exit load of UTI Flexi Cap Fund?"*, *"How to request an HDFC account statement?"*).
     - Response layout displaying the text (max 3 sentences), an icon-styled citation badge linking to the source URL, and the extraction date in the footer.
3. **Database Scheduler Integration (`src/scheduler.py`)**:
   - Write a scheduling module containing a thread-based background clock loop that checks the current time.
   - Schedule database updates daily at **09:25 AM**.
   - Upon trigger, run the scraper ingestion pipeline (`src/ingest.py`) followed by the vector builder pipeline (`src/index_builder.py`) to scrape, clean, and rebuild the vector database and `chunks.json` files.
   - Integrate and trigger the scheduler as a non-blocking background thread within the FastAPI startup lifecycle in `src/app.py`.

---

## Phase 6: Testing & Quality Assurance
**Goal**: Test and validate system compliance, accuracy, and format boundaries.

### Evaluation Checklist
- [ ] **Data Completeness**: Verify that schemes for all 10 AMCs listed in `groww_amcs.json` are fully queried and returned correctly.
- [ ] **Advisory Deflection**: Send 10+ subjective queries (e.g., *"Is Tata Small Cap a good buy?"*, *"Suggest a fund with 15% returns"*) and ensure polite refusal + educational link redirection.
- [ ] **Privacy Guard**: Send 10+ queries containing varying formats of PAN, Aadhaar, fake bank accounts, or OTP tags, ensuring they are blocked before calling the LLM.
- [ ] **Output Constraints**: Confirm that all successful query responses are strictly $\le 3$ sentences, feature exactly one reference URL, and include the `Last updated from sources: <date>` footer.

