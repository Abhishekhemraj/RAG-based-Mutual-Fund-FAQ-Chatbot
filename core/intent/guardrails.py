import re

class PersonalDataGuard:
    """Detects and blocks PII (Personal Identifiable Information)."""
    
    # regex patterns for sensitive data
    PII_PATTERNS = {
        "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
        "Aadhaar": r"\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b",
        "BankAcc": r"\b[0-9]{9,18}\b",
        "Phone": r"\b[0-9]{10}\b",
        "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    }

    def contains_pii(self, text):
        for label, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, text):
                return True, label
        return False, None

class IntentClassifier:
    """Identifies and blocks out-of-scope or advisory queries."""
    
    ADVISORY_KEYWORDS = ["best", "invest", "buy", "sell", "advice", "recommend", "predict", "should i", "suggestion"]
    
    def classify_intent(self, text):
        text = text.lower()
        
        # Performance/Comparison Check (Redirect rule)
        performance_keywords = ["compare", "returns", "comparison", "performance", "outperformed", "underperformed", "vs", "versus", "yield", "growth %"]
        if any(kw in text for kw in performance_keywords):
            return "performance_query"
            
        # Advisory Check
        if any(kw in text for kw in self.ADVISORY_KEYWORDS):
            return "advisory"
            
        # Basic Mutual Fund/Scheme/Service Check
        if any(kw in text for kw in ["tata", "fund", "scheme", "nav", "exit load", "expense", "sip", "elss", "statement", "folio", "download"]):
            return "factual"
            
        return "out_of_scope"

def process_guardrails(query):
    guard = PersonalDataGuard()
    pii_found, label = guard.contains_pii(query)
    
    if pii_found:
        return False, f"Privacy Alert: Please do not provide sensitive information like {label}. I cannot process your request for security reasons."
    
    classifier = IntentClassifier()
    intent = classifier.classify_intent(query)
    
    if intent == "advisory":
        return False, "I am only able to provide factual information about schemes. For investment advice or recommendations, please consult a SEBI-registered advisor."
    
    if intent == "performance_query":
        # Specific redirect rule for performance queries
        return False, "I cannot compute or compare fund performance. Please refer to the official factsheet at https://www.tatamutualfund.com/factsheets for official performance metrics."
        
    if intent == "out_of_scope":
        return False, "I only respond to Tata Mutual Fund scheme-related queries. How can I help you with details like NAV, Exit Load, or SIP of Tata funds?"
        
    return True, "factual"
