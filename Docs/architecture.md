# Architecture Design: Mutual Fund FAQ Assistant

This document details the architectural layout, data flow, and components of the **Mutual Fund FAQ Assistant (Facts-Only Q&A)**. The system is designed around a lightweight, high-precision Retrieval-Augmented Generation (RAG) framework equipped with strict compliance and privacy guardrails.

---

## 1. High-Level Component Architecture

The application is structured into three primary tiers: the **User Interface (Presentation Layer)**, the **Orchestration & Guardrails Layer (Application backend)**, and the **Retrieval & Storage Layer (Data Layer)**.

```mermaid
graph TB
    subgraph Presentation Layer
        UI[Minimal Web Interface]
    end

    subgraph Application & Guardrails Layer
        Controller[Backend Orchestrator]
        Classifier{Query Classifier}
        PIIDetector{PII Scanner}
        LLM[LLM Generation Engine]
        PostProcessor[Compliance Validator]
    end

    subgraph Data & Retrieval Layer
        VectorStore[(Vector Store / Search Index)]
        Corpus[(Curated Corpus: KIM/SID/Factsheets)]
    end

    %% User Interaction Flow
    UI -->|1. Submit Query| Controller
    Controller -->|2. Route Query| Classifier
    
    %% Guardrail Decisions
    Classifier -->|Advisory / Out-of-Scope| Refusal[Refusal Engine]
    Classifier -->|Factual Query| PIIDetector
    
    PIIDetector -->|Contains PII| PIIHandler[PII Warning & Redaction]
    PIIDetector -->|Clean Factual| VectorStore
    
    %% RAG Retrieval & Gen
    VectorStore -->|3. Query Vector Index| Corpus
    Corpus -->|4. Return Context Chunks| Controller
    Controller -->|5. Context + Prompt| LLM
    LLM -->|6. Generate Raw Response| PostProcessor
    PostProcessor -->|7. Verified Response & Source Link| UI

    %% Fallback paths
    Refusal --> UI
    PIIHandler --> UI
```

---

## 2. Core Components Detail

### A. Presentation Layer (Minimal Web UI)
A simple, state-of-the-art conversational interface utilizing Vanilla HTML/CSS/JS.
- **Features**:
  - Visible global disclaimer: `"Facts-only. No investment advice."`
  - Starter questions for quick exploration.
  - Streaming conversational display.
  - Formatted citations showing active source links and the last-updated date footer.

### B. Application & Guardrails Layer
This layer operates as the control tower for inputs, routing, and processing compliance.
1. **Query Classifier**: Evaluates whether incoming prompts seek objective facts or advisory/subjective guidance.
   - *Factual Examples*: "What is the exit load of Fund X?", "Who is the fund manager of Fund Y?"
   - *Advisory Examples*: "Which fund is best for tax saving?", "Should I buy ICICI Prudential Bluechip?"
2. **PII Scanner**: Leverages deterministic rules (regex) to intercept queries containing sensitive user credentials (such as PAN, Aadhaar, folio numbers, bank accounts, or OTPs) and returns a privacy refusal message before calling downstream AI models.
3. **LLM Generation Engine**: Utilizes a highly constrained prompt system instructing the LLM to write replies strictly from the provided context.
4. **Post-Processor**: Asserts formatting constraints:
   - Output lengths are restricted to $\le 3$ sentences.
   - Verifies the inclusion of exactly one citation URL and the `Last updated` timestamp.

### C. Data & Retrieval Layer
- **Curated Corpus**: A JSON/Markdown database indexing official documents from the selected AMC (e.g. KIM, SID, Factsheets, and download page guides).
- **Search Index / Vector Database**: Contains tokenized and embedded document chunks to run semantic or keyword searches. Since the corpus is small (15–25 documents), a lightweight vector store like ChromaDB, FAISS, or even a local metadata index is used.

---

## 3. Detailed Data Flow Trace

Below is the lifecycle of a request from client input to response generation:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Web Client
    participant API as FastAPI Backend
    participant Guard as Guardrails Engine
    participant DB as Vector Store
    participant LLM as LLM API

    User ->> UI: Ask: "What is the exit load of HDFC Top 100?"
    UI ->> API: HTTP POST /api/query { "query": "..." }
    
    API ->> Guard: Validate Query (Advisory & PII checks)
    Note over Guard: Checks if query has PAN/Aadhaar/OTP or asks for opinion
    Guard -->> API: Valid Factual Query
    
    API ->> DB: Query embeddings (KIM, SID, factsheets)
    DB -->> API: Return Top K Context Chunks + Source Metadata
    
    API ->> LLM: Send prompt (Query + Context Chunks + Constraints)
    Note over LLM: Formulate response in max 3 sentences.<br/>Inject official link & last-updated footer.
    LLM -->> API: Return response text
    
    API ->> UI: Stream JSON { "answer": "...", "source": "...", "last_updated": "..." }
    UI ->> User: Display Answer & Citations
```

---

## 4. Ingestion & Pre-processing Pipeline

To prepare the retrieval index, we process the official public URLs using an offline ingestion pipeline:

```mermaid
flowchart LR
    A[Official AMC URLs] --> B[Web Scraper / PDF Downloader]
    B --> C[Text Extraction & Cleaning]
    C --> D[Text Chunking & Embedding Generation]
    D --> E[(Vector Store Indexing)]
    
    subgraph Metadata Tagging
        F[Attach Source URL]
        G[Attach Extraction Date]
    end
    C --> F
    C --> G
```

- **Chunking Strategy**: Overlapping recursive character splitter (e.g. chunk size: 512 tokens, overlap: 64 tokens) to maintain search contextual accuracy across numbers, tables, and clauses in factsheets.
- **Data Cleaning & Sanitization**: Strips HTML boilerplates (such as `script`, `style`, `meta`, `header`, `footer`, `nav`, and `noscript` tags) during ingestion using BeautifulSoup. Text segments are parsed, whitespaces are normalized, and irrelevant short lines (under 30 characters) containing menu/button noise are filtered out.
- **Source Mapping**: Every chunk is tagged with its origin file name, public URL, and download timestamp to ensure citation fidelity.
- **Automated Update Scheduler**: A background scheduling daemon (which runs as a background thread started on web-server startup) triggers database refreshes every day at **09:25 AM**. It executes the scraping ingest module (`src/ingest.py`) followed by the vector builder module (`src/index_builder.py`) to keep local data files and vector embeddings synchronized with upstream changes.

---

## 5. Security & Regulatory Compliance Guardrails

As a financial tool, the assistant enforces strict boundary controls:

| Risk Area | Mitigating Guardrail Design |
|---|---|
| **Investment Advice / Opinion** | The Classifier rejects subjective terms (*"better", "should I", "recommend"*) and redirects the user with educational links. |
| **Out-of-Scope RAG Hallucinations** | If the retrieval similarity score is below a predefined threshold, the assistant falls back to a polite refusal: *"I cannot find official source documents for this request."* |
| **Privacy Leakage (PII)** | Incoming text is scanned via regex patterns for Aadhaar (`[2-9]{1}[0-9]{3}\\s[0-9]{4}\\s[0-9]{4}`), PAN (`[A-Z]{5}[0-9]{4}[A-Z]{1}`), and generic account details, stopping processing immediately if flagged. |
| **Data Recency** | The system automatically appends the database build date as the `Last updated from sources: <date>` footer, ensuring users know the age of the data. |
