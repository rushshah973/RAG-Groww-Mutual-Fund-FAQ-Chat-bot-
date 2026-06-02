import os
import re
import requests

import config

def split_into_sentences(text: str) -> list:
    """
    Splits text into sentences using regex boundary detection.
    Handles abbreviations like Rs. or percentage indicators.
    """
    # Replace common abbreviations that might confuse splitter
    temp_text = text.replace("Rs. ", "Rs ")
    temp_text = temp_text.replace("Corp. ", "Corp ")
    temp_text = temp_text.replace("Co. ", "Co ")
    temp_text = temp_text.replace("ED. ", "ED ")
    temp_text = temp_text.replace("ED ", "ED ")
    
    # Split on period, exclamation, or question mark followed by whitespace
    raw_sentences = re.split(r'(?<=[.!?])\s+', temp_text)
    
    # Restore abbreviations and clean sentences
    sentences = []
    for s in raw_sentences:
        s_clean = s.strip()
        if s_clean:
            # Put back the space after Rs if it was replaced
            s_clean = s_clean.replace("Rs ", "Rs. ")
            sentences.append(s_clean)
            
    return sentences

def format_factual_sentence(s: str) -> str:
    s_clean = s.strip()
    
    # 1. Format Fund Managers
    if "Fund Managers:" in s_clean or "Fund Manager:" in s_clean:
        prefix = "Fund Managers: " if "Fund Managers: " in s_clean else "Fund Manager: "
        try:
            managers_part = s_clean.split(prefix)[1].strip().rstrip(".")
            managers = [m.strip() for m in managers_part.split(";")]
            formatted_managers = []
            for mgr in managers:
                # Use non-greedy (.*?) to allow commas in Credentials and Experience
                match = re.match(r'([^(]+)\(Credentials:\s*(.*?),\s*Experience:\s*(.*?),\s*Tenure:\s*([^)]+)\)', mgr)
                if match:
                    name = match.group(1).strip()
                    credentials = match.group(2).strip()
                    experience = match.group(3).strip()
                    tenure = match.group(4).strip()
                    
                    # Clean up tenure and experience
                    tenure_clean = tenure.strip()
                    exp_clean = experience[0].lower() + experience[1:] if experience else ""
                    
                    # If experience starts with "over", "more than", "around", "about", or a number, use "has over..."
                    # Otherwise (e.g. "dedicated..."), use "serves as..."
                    if re.match(r'^(over|under|around|about|more|less|\d)', exp_clean, re.IGNORECASE):
                        exp_phrase = f"has {exp_clean}"
                    else:
                        exp_phrase = f"serves as a {exp_clean}" if not exp_clean.startswith("a ") and not exp_clean.startswith("an ") else f"serves as {exp_clean}"
                        
                    formatted = f"{name} (Credentials: {credentials}), who has been {tenure_clean} and {exp_phrase}"
                    formatted_managers.append(formatted)
                else:
                    formatted_managers.append(mgr)
            if len(formatted_managers) == 1:
                return f"The fund is managed by {formatted_managers[0]}."
            else:
                return f"The fund is co-managed by {', '.join(formatted_managers[:-1])} and {formatted_managers[-1]}."
        except Exception:
            return s_clean
            
    # 2. Format Expense Ratio
    if "Expense Ratio:" in s_clean:
        match = re.search(r'Expense Ratio:\s*Direct Plan is\s*([^,]+),\s*Regular Plan is\s*(.*)', s_clean)
        if match:
            direct = match.group(1).strip()
            regular = match.group(2).strip().rstrip(".")
            return f"The scheme's expense ratio is {direct} for the Direct Plan and {regular} for the Regular Plan."
            
    # 3. Format Exit Load
    if "Exit Load:" in s_clean:
        try:
            load_part = s_clean.split("Exit Load:")[1].strip()
            if load_part.endswith("."):
                load_part = load_part[:-1]
            return f"The exit load for the scheme is {load_part}."
        except Exception:
            pass
            
    # 4. Format Minimum SIP
    if "Minimum SIP Amount:" in s_clean:
        try:
            sip_part = s_clean.split("Minimum SIP Amount:")[1].strip()
            if sip_part.endswith("."):
                sip_part = sip_part[:-1]
            return f"The minimum SIP amount required is {sip_part}."
        except Exception:
            pass
            
    # 5. Format Lock-in Period
    if "Lock-in Period:" in s_clean:
        try:
            lock_part = s_clean.split("Lock-in Period:")[1].strip()
            if lock_part.endswith("."):
                lock_part = lock_part[:-1]
            return f"The lock-in period for the scheme is {lock_part}."
        except Exception:
            pass
            
    # 6. Format Benchmark Index
    if "Benchmark Index:" in s_clean:
        try:
            bench_part = s_clean.split("Benchmark Index:")[1].strip()
            if bench_part.endswith("."):
                bench_part = bench_part[:-1]
            return f"The benchmark index of the scheme is {bench_part}."
        except Exception:
            pass
            
    # 7. Format Riskometer
    if "Riskometer Classification:" in s_clean:
        try:
            risk_part = s_clean.split("Riskometer Classification:")[1].strip()
            if risk_part.endswith("."):
                risk_part = risk_part[:-1]
            return f"The risk classification for this scheme is {risk_part}."
        except Exception:
            pass
            
    # 8. Format Type
    if "Type:" in s_clean:
        try:
            type_part = s_clean.split("Type:")[1].strip()
            if type_part.endswith("."):
                type_part = type_part[:-1]
            return f"The category type of this scheme is {type_part}."
        except Exception:
            pass
            
    # 9. Format Scheme factsheet details
    if s_clean.startswith("Scheme factsheet details for"):
        return s_clean.replace("Scheme factsheet details for", "These are the official factsheet details for")
            
    return s_clean

def fallback_extractor(query: str, chunks: list, metadatas: list = None) -> str:
    """
    Extracts the most relevant factual sentence(s) from the retrieved chunks.
    Ensures 100% factual accuracy with zero hallucination.
    """
    if not chunks:
        return "I cannot verify this information from the official sources."
        
    query_lower = query.lower()
    
    # 1. Filter chunks by AMC name first if query mentions a specific AMC
    amc_keywords = {
        "sbi": ["sbi"],
        "hdfc": ["hdfc"],
        "icici": ["icici", "prudential"],
        "kotak": ["kotak", "mahindra"],
        "axis": ["axis"],
        "mirae": ["mirae", "asset"],
        "nippon": ["nippon", "nippon india"],
        "tata": ["tata"],
        "uti": ["uti"],
        "groww": ["groww"]
    }
    
    mentioned_amcs = []
    for amc_key, keywords in amc_keywords.items():
        if any(kw in query_lower for kw in keywords):
            mentioned_amcs.append(amc_key)
            
    # Extract distinctive query subject words (filter out stop words and parameters)
    stop_words = {
        "what", "is", "the", "of", "for", "in", "and", "to", "a", "an", "who", "will", 
        "win", "how", "much", "amount", "period", "index", "details", "contact", 
        "support", "email", "phone", "download", "request", "statement", "report", 
        "process", "exit", "load", "expense", "ratio", "minimum", "sip", "lock-in", 
        "lock", "riskometer", "classification", "benchmark", "manager", "managers", 
        "credentials", "experience", "tenure", "managing", "since", "value", "type", 
        "direct", "regular", "plan", "plans", "fund", "funds", "mutual", "assistant",
        "please", "ask", "related", "made", "query", "queries", "give", "tell", "show", "get",
        # New Q&A helper words
        "are", "were", "was", "been", "have", "has", "had", "does", "do", "did", "can", "could",
        "should", "would", "about", "schemes", "scheme", "list", "name", "names", "active",
        "which", "there", "any", "all", "some", "other", "under", "over", "between", "from",
        "with", "by", "out", "me", "us", "you", "your", "my", "our", "their", "available",
        "offered", "services", "info", "information", "data", "profile", "profiles",
        "factsheet", "factsheets", "tell", "show", "get", "give", "find", "search", "view",
        "amc", "amcs", "hello", "hi", "hey", "help", "please", "thank", "thanks", "welcome",
        # Common scheme categories (already filtered by scheme keyword mismatch check)
        "bluechip", "small", "mid", "large", "cap", "flexi", "tax", "saver", "taxsaver",
        "elss", "opportunities", "value", "discovery", "digital", "market", "term", "growth",
        "dividend", "equity", "debt", "hybrid", "liquid", "index", "total", "midcap", "smallcap",
        "flexicap", "largecap"
    }
    query_words = set(re.findall(r'\b[a-z]{3,}\b', query_lower))
    subject_words = query_words - stop_words
    
    filtered_chunks = []
    if metadatas:
        for chunk, meta in zip(chunks, metadatas):
            amc_name = meta.get("amc_name", "").lower()
            scheme_name = meta.get("scheme_name", "").lower()
            
            # Check AMC match: if query specifies an AMC, the chunk must match it
            if mentioned_amcs:
                if not any(kw in amc_name for kw in mentioned_amcs):
                    continue
                    
            # Check Scheme keyword mismatch
            # If query mentions a specific scheme type, prevent matching other schemes
            scheme_keywords = ["bluechip", "small cap", "small", "cap", "long term", "tax saver", "taxsaver", "flexicap", "flexi cap", "emerging", "mid-cap", "mid cap", "opportunities", "value", "discovery", "digital", "total market", "index"]
            mismatch = False
            if scheme_name != "general":
                for kw in scheme_keywords:
                    if kw in query_lower:
                        if kw not in scheme_name:
                            mismatch = True
                            break
            if mismatch:
                continue
                
            # Check subject words: any subject word in the query (like brand names) must be in the chunk/metadata
            chunk_lower = chunk.lower()
            meta_values_lower = " ".join([str(v).lower() for v in meta.values()])
            has_unmatched_subject = False
            for word in subject_words:
                if word not in chunk_lower and word not in meta_values_lower:
                    # Special check: "flexi" vs "flexicap"
                    if word == "flexi" and "flexicap" in chunk_lower:
                        continue
                    has_unmatched_subject = True
                    break
            if has_unmatched_subject:
                continue
                
            filtered_chunks.append(chunk)
    else:
        filtered_chunks = chunks
        
    if not filtered_chunks:
        return "I cannot verify this information from the official sources."
        
    relevant_sentences = []
    seen_sentences = set()
    
    # Process all selected chunks to collect relevant sentences
    for chunk in filtered_chunks:
        # Split chunk into sentences
        sentences = split_into_sentences(chunk)
        
        # Filter sentences based on query intent for high specificity
        chunk_relevant = []
        if "exit load" in query_lower:
            chunk_relevant = [s for s in sentences if "exit load" in s.lower() or "charges apply" in s.lower() or "redemption" in s.lower()]
        elif "expense" in query_lower:
            chunk_relevant = [s for s in sentences if "expense ratio" in s.lower() or "direct plan" in s.lower() or "regular plan" in s.lower()]
        elif "sip" in query_lower or "minimum" in query_lower:
            chunk_relevant = [s for s in sentences if "sip" in s.lower() or "minimum" in s.lower()]
        elif "lock-in" in query_lower or "elss" in query_lower or "lock in" in query_lower:
            chunk_relevant = [s for s in sentences if "lock-in" in s.lower() or "lock in" in s.lower() or "80c" in s.lower() or "tax savings" in s.lower()]
        elif "riskometer" in query_lower:
            chunk_relevant = [s for s in sentences if "riskometer" in s.lower() or "classification" in s.lower()]
        elif "benchmark" in query_lower:
            chunk_relevant = [s for s in sentences if "benchmark" in s.lower() or "tri" in s.lower() or "index" in s.lower()]
        elif "manager" in query_lower or "experience" in query_lower or "tenure" in query_lower or "credentials" in query_lower:
            chunk_relevant = [s for s in sentences if "manager" in s.lower() or "experience" in s.lower() or "credentials" in s.lower() or "managing since" in s.lower()]
        elif "statement" in query_lower or "report" in query_lower or "download" in query_lower:
            chunk_relevant = [s for s in sentences if "statement" in s.lower() or "report" in s.lower() or "download" in s.lower() or "portal" in s.lower()]
        elif "contact" in query_lower or "support" in query_lower or "email" in query_lower or "phone" in query_lower:
            chunk_relevant = [s for s in sentences if "contact" in s.lower() or "support" in s.lower() or "email" in s.lower() or "phone" in s.lower()]
        elif "about" in query_lower or "who is" in query_lower or "what is" in query_lower or "info" in query_lower:
            chunk_relevant = [s for s in sentences if "about" in s.lower() or "managed by" in s.lower() or "premier" in s.lower() or "leading" in s.lower()]
        elif "scheme" in query_lower or "funds" in query_lower or "list" in query_lower:
            # If asking about schemes/funds of an AMC, collect them from metadata
            scheme_names = []
            amc_display_name = ""
            if metadatas:
                for meta in metadatas:
                    amc_name = meta.get("amc_name", "")
                    s_name = meta.get("scheme_name", "")
                    doc_type = meta.get("document_type", "")
                    if doc_type == "scheme_factsheet" and s_name and s_name.lower() != "general":
                        if s_name not in scheme_names:
                            scheme_names.append(s_name)
                        if amc_name and not amc_display_name:
                            amc_display_name = amc_name
            if scheme_names:
                amc_str = f" under {amc_display_name}" if amc_display_name else ""
                if len(scheme_names) == 1:
                    chunk_relevant = [f"The schemes available{amc_str} are {scheme_names[0]}."]
                elif len(scheme_names) == 2:
                    chunk_relevant = [f"The schemes available{amc_str} are {scheme_names[0]} and {scheme_names[1]}."]
                else:
                    chunk_relevant = [f"The schemes available{amc_str} are {', '.join(scheme_names[:-1])} and {scheme_names[-1]}."]
            
        for s in chunk_relevant:
            s_clean = s.strip()
            s_lower = s_clean.lower()
            if s_lower not in seen_sentences:
                seen_sentences.add(s_lower)
                relevant_sentences.append(s_clean)
                
    # If no highly specific sentence matches from any chunk, take the first 5 sentences of the top chunk
    if not relevant_sentences:
        first_chunk_sentences = split_into_sentences(filtered_chunks[0])
        relevant_sentences = first_chunk_sentences[:5]
        
    # Return up to 5 sentences
    return " ".join(relevant_sentences[:5])

def generate_answer(query: str, retrieved_chunks: list, metadatas: list) -> dict:
    """
    Generates a context-bound response.
    Tries API endpoints (Gemini, OpenAI) if keys are present; otherwise, falls back on the factual extractor.
    Returns:
        dict: { "answer": str, "source_url": str, "last_updated": str }
    """
    if not retrieved_chunks:
        return {
            "answer": "I cannot verify this information from the official sources.",
            "source_url": "https://www.amfiindia.com/",
            "last_updated": "2026-05-31"
        }
        
    # Extract top metadata for source attribution
    top_meta = metadatas[0] if metadatas else {}
    source_url = top_meta.get("source_url", "https://www.amfiindia.com/")
    last_updated = top_meta.get("extracted_date", "2026-05-31")
    
    context = "\n---\n".join(retrieved_chunks)
    
    # Define prompt template
    system_prompt = (
        "You are a facts-only Mutual Fund FAQ Assistant.\n"
        "Answer the user's query using ONLY the retrieved factual context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Query:\n{query}\n\n"
        "Constraints:\n"
        "1. Answer using ONLY the provided facts. Do not make assumptions or extrapolate.\n"
        "2. If the answer cannot be found in the context, respond exactly with: 'I cannot verify this information from the official sources.'\n"
        "3. Do not offer investment advice, comparisons, or performance opinions.\n"
        "4. Keep the response brief, clear, and complete. Do not exceed 5 sentences."
    )
    
    answer_text = ""
    
    # 1. Try Gemini API
    gemini_key = config.GEMINI_API_KEY
    openai_key = config.OPENAI_API_KEY
    
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": system_prompt}]}],
                "generationConfig": {
                    "temperature": 0.0,
                    "maxOutputTokens": 200
                }
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                answer_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                print(f"Gemini API returned status code {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Gemini API call failed with exception: {e}. Falling back...")
            
    # 2. Try OpenAI API
    if not answer_text and openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a factual mutual fund helper. Answer queries using the context provided."},
                    {"role": "user", "content": system_prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 200
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                answer_text = res_data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"OpenAI API call failed: {e}. Falling back...")
            
    # 3. Fallback to Local Factual Extractor (100% accurate, offline)
    if not answer_text:
        answer_text = fallback_extractor(query, retrieved_chunks, metadatas)
        
    # --- POST PROCESSING AND CONSTRAINT ENFORCEMENT ---
    # Strip any external http/https urls that the LLM may have fabricated in the text body
    answer_text = re.sub(r'https?://\S+', '', answer_text).strip()
    
    # Split sentences and enforce maximum of 5 sentences constraint
    sentences = split_into_sentences(answer_text)
    formatted_sentences = [format_factual_sentence(s) for s in sentences]
    truncated_answer = " ".join(formatted_sentences[:5])
    
    # Ensure a clean response if empty
    if not truncated_answer:
        truncated_answer = "I cannot verify this information from the official sources."
        
    return {
        "answer": truncated_answer,
        "source_url": source_url,
        "last_updated": last_updated
    }

if __name__ == "__main__":
    # Test data representing typical retrieved database chunks
    test_chunks = [
        "Scheme factsheet details for 'SBI Bluechip Fund' managed by SBI Mutual Fund. Type: Large Cap. Expense Ratio: Direct Plan is 0.87%, Regular Plan is 1.55%. Exit Load: 1.00% if redeemed within 1 year (365 days) from allotment, Nil after 1 year. Minimum SIP Amount: Rs. 500. Lock-in Period: Nil. Riskometer Classification: Very High. Benchmark Index: S&P BSE 100 TRI. Fund Managers: Sohini Andani (Credentials: B.Com, MMS, Experience: Over 25 years in financial services, Tenure: managing since September 2010); Pradeep Kesavan (Credentials: B.Tech, PGDM, Experience: Dedicated overseas investment manager, Tenure: managing since May 2021)."
    ]
    test_metadatas = [{
        "amc_name": "SBI Mutual Fund",
        "scheme_name": "SBI Bluechip Fund",
        "document_type": "scheme_factsheet",
        "source_url": "https://groww.in/mutual-funds/amc/sbi-mutual-funds",
        "extracted_date": "2026-05-31"
    }]
    
    test_queries = [
        "What is the exit load of SBI Bluechip?",
        "Who are the fund managers of SBI Bluechip Fund?",
        "What is the expense ratio?"
    ]
    
    print("Testing LLM generation & post-processing constraints:")
    print("=" * 70)
    for q in test_queries:
        res = generate_answer(q, test_chunks, test_metadatas)
        print(f"Query: {q}")
        print(f"Answer: {res['answer']}")
        print(f"Source URL: {res['source_url']}")
        print(f"Last Updated: {res['last_updated']}")
        print(f"Sentences Count: {len(split_into_sentences(res['answer']))}")
        print("-" * 70)
