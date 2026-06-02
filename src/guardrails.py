import re

# PII Regex Patterns
AADHAAR_PATTERN = re.compile(r'\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b')
PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.IGNORECASE)
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b')

# Numeric sequence of 4 to 18 digits (used for folio, bank account, OTP detection)
NUMERIC_SEQUENCE_PATTERN = re.compile(r'\b\d{4,18}\b')

# Keywords triggering specific PII context checks
PII_KEYWORDS = ['folio', 'account', 'otp', 'one time password', 'pin', 'bank', 'pwd', 'password', 'login']

# Advisory keywords and phrases
ADVISORY_KEYWORDS = [
    r'\bshould\s+i\b',
    r'\bwhich\s+(?:is|are|would\s+be).*\s+better\b',
    r'\bwhich\s+(?:is|are|would\s+be).*\s+best\b',
    r'\bbest\s+fund\b',
    r'\bbest\s+mutual\s+fund\b',
    r'\brecommend\b',
    r'\bsuggest\b',
    r'\badvice\b',
    r'\badvise\b',
    r'\bwhere\s+should\s+i\s+invest\b',
    r'\bwhere\s+to\s+invest\b',
    r'\bmaximize\s+returns\b',
    r'\btop\s+(?:performing|rated)\b',
    r'\bwill\s+i\s+get\b',
    r'\bwill\s+it\s+make\s+me\b',
    r'\bcompare\b',
    r'\bcomparison\b',
    r'\bwhich\s+one\s+to\s+(?:buy|invest)\b',
    r'\bhow\s+much\s+returns\b',
    r'\bexpected\s+returns\b',
    r'\bportfolio\s+review\b',
    r'\bperformance\s+of\b',
    r'\bbetter\s+fund\b',
    r'\bbetter\s+option\b'
]
ADVISORY_PATTERNS = [re.compile(p, re.IGNORECASE) for p in ADVISORY_KEYWORDS]

# Relevance keywords mapping for out-of-scope deflection
RELEVANCE_KEYWORDS = [
    # Core terms
    "fund", "scheme", "amc", "mutual", "portfolio", "sip", "exit load", "expense",
    "ratio", "minimum", "lock-in", "lock in", "riskometer", "benchmark", "index",
    "manager", "statement", "report", "download", "tax", "80c", "capital gain",
    "folio", "support", "contact", "phone", "email", "address", "servicing", "invest",
    "plan", "plans", "direct", "regular", "growth", "dividend", "idcw",
    # AMC Names
    "sbi", "hdfc", "icici", "kotak", "axis", "mirae", "nippon", "tata", "uti", "groww",
    # Scheme names
    "bluechip", "small cap", "long term", "equity", "tax saver", "flexicap", "flexi cap",
    "emerging", "mid-cap", "mid cap", "opportunities", "value", "discovery", "digital",
    "total market", "contra", "multi asset", "multi-asset", "gold", "silver",
    # Managers names
    "sohini", "andani", "pradeep", "kesavan", "srinivasan", "dinesh", "balachandran",
    "gopal", "agrawal", "chirag", "setalvad", "roshi", "jain", "anish", "tawakley",
    "rajat", "chandak", "sankaran", "naren", "harish", "bihani", "harsha", "upadhyaya",
    "pankaj", "tibrewal", "shreyash", "devalkar", "jinesh", "gopani", "mahendra", "jajoo",
    "vrijesh", "kasera", "neelesh", "surana", "ankit", "pandey", "sailesh", "raj",
    "bhanushali", "vetri", "subramaniam", "swati", "kulkarni", "abhishek", "ashish", "naik",
    "rahul", "singh", "chandraprakash", "padiyar"
]

def scan_relevance(query: str) -> dict:
    """
    Checks if the user query is related to mutual funds or greetings.
    Deflects out-of-scope queries.
    """
    query_lower = query.lower()
    
    # Check greetings first
    greetings = ['hi', 'hello', 'hey', 'help', 'greetings', 'hola', 'yo']
    clean_query = re.sub(r'[^\w\s]', '', query_lower).strip()
    if clean_query in greetings:
        return {
            "violated": True,
            "type": "unrelated",
            "message": "Hello! I am the Groww Mutual Fund FAQ Assistant. I can help you find factual details about mutual fund schemes, such as exit loads, expense ratios, fund managers, minimum SIPs, lock-in periods, or account statements. How can I help you today?"
        }
        
    # Check if any relevance keyword matches
    has_match = False
    for kw in RELEVANCE_KEYWORDS:
        if kw in query_lower:
            has_match = True
            break
            
    if not has_match:
        return {
            "violated": True,
            "type": "unrelated",
            "message": "I can only answer factual questions related to mutual funds (such as exit loads, expense ratios, fund managers, minimum SIPs, lock-in periods, or account statements). Please ask a question related to mutual funds."
        }
        
    return {"violated": False}

def scan_pii(query: str) -> dict:
    """
    Scans the user query for personal identifiable information (PII).
    Returns a dict with 'violated': bool and 'message': str if violated.
    """
    # Check direct Aadhaar match
    if AADHAAR_PATTERN.search(query):
        return {
            "violated": True,
            "type": "pii",
            "message": "For security and privacy reasons, please do not share personally identifiable information (PII) such as PAN, Aadhaar, folio numbers, bank details, or OTPs. Transaction aborted."
        }
        
    # Check direct PAN match
    if PAN_PATTERN.search(query):
        return {
            "violated": True,
            "type": "pii",
            "message": "For security and privacy reasons, please do not share personally identifiable information (PII) such as PAN, Aadhaar, folio numbers, bank details, or OTPs. Transaction aborted."
        }
        
    # Check direct Email match
    if EMAIL_PATTERN.search(query):
        return {
            "violated": True,
            "type": "pii",
            "message": "For security and privacy reasons, please do not share personally identifiable information (PII) such as email addresses, phone numbers, or account details. Transaction aborted."
        }
        
    # Check direct Phone match
    if PHONE_PATTERN.search(query):
        return {
            "violated": True,
            "type": "pii",
            "message": "For security and privacy reasons, please do not share personally identifiable information (PII) such as phone numbers, account details, or bank credentials. Transaction aborted."
        }
        
    # Context-based check: if query has terms like 'folio', 'otp', 'account' AND a number of length 4-18
    query_lower = query.lower()
    has_pii_keyword = any(kw in query_lower for kw in PII_KEYWORDS)
    if has_pii_keyword and NUMERIC_SEQUENCE_PATTERN.search(query):
        return {
            "violated": True,
            "type": "pii",
            "message": "For security and privacy reasons, please do not share personally identifiable information (PII) such as PAN, Aadhaar, folio numbers, bank details, or OTPs. Transaction aborted."
        }
        
    return {"violated": False}

def scan_advisory(query: str) -> dict:
    """
    Scans the user query for advisory or out-of-scope intent.
    Returns a dict with 'violated': bool and 'message': str if violated.
    """
    query_lower = query.lower()
    
    # Check advisory patterns
    for pattern in ADVISORY_PATTERNS:
        if pattern.search(query_lower):
            return {
                "violated": True,
                "type": "advisory",
                "message": "I can only provide objective, facts-only information about mutual fund schemes. I cannot provide investment advice, comparisons, or recommendations. For educational resources on mutual funds, please visit the [AMFI Investor Corner](https://www.amfiindia.com/investor-corner/knowledge-center/tax-benefits.html) or [SEBI Investor Education](https://investor.sebi.gov.in/)."
            }
            
    return {"violated": False}

def validate_query(query: str) -> dict:
    """
    Runs Relevance, PII, and Advisory checks.
    Returns a dict detailing the validation status.
    """
    # 1. Relevance Scan
    relevance_result = scan_relevance(query)
    if relevance_result["violated"]:
        return {
            "status": "violated",
            "type": relevance_result["type"],
            "message": relevance_result["message"]
        }
        
    # 2. PII Scan
    pii_result = scan_pii(query)
    if pii_result["violated"]:
        return {
            "status": "violated",
            "type": "pii",
            "message": pii_result["message"]
        }
        
    # 3. Advisory Scan
    advisory_result = scan_advisory(query)
    if advisory_result["violated"]:
        return {
            "status": "violated",
            "type": "advisory",
            "message": advisory_result["message"]
        }
        
    return {
        "status": "clean",
        "type": None,
        "message": "Query is clean and factual."
    }

if __name__ == "__main__":
    # Quick sanity test cases
    test_queries = [
        "What is the exit load of SBI Bluechip?",
        "Should I invest in HDFC Top 100?",
        "My PAN is ABCDE1234F, what is my balance?",
        "How do I request an Axis statement?",
        "Here is my verification OTP 123456",
        "Send the report to contact@user.com",
        "Which is a better fund: SBI Small Cap or HDFC Mid-cap?"
    ]
    
    print("Running Guardrails Verification tests:")
    print("=" * 60)
    for q in test_queries:
        res = validate_query(q)
        print(f"Query: '{q}'")
        print(f"Status: {res['status']}, Type: {res['type']}")
        if res['status'] == 'violated':
            print(f"Message: {res['message']}")
        print("-" * 60)
