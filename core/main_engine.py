import os
import sys

# Ensure parent folder for imports is available
sys.path.append(os.getcwd())

from core.intent.guardrails import process_guardrails
from core.llm.groq_handler import GroqRAGHandler
from indexing.embedders.hf_embedder import HFEmbedder
from indexing.vector_store.faiss_store import FAISSStore
from config import indexing_config

class TataMF_Chatbot:
    """Ties all phases together: Ingestion -> Indexing -> Guardrails -> Groq."""
    
    def __init__(self, api_key=None):
        self.embedder = HFEmbedder(indexing_config.EMBEDDING_MODEL_NAME)
        self.vector_store = FAISSStore(dimension=384, index_path=indexing_config.VECTOR_DB_PATH)
        
        # Load index
        self.vector_store.load_index(indexing_config.FAISS_INDEX_NAME)
        
        # LLM Integration
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.llm = None
        if self.api_key:
             self.llm = GroqRAGHandler(api_key=self.api_key)

    def ask(self, query):
        """Unified Phase 4 RAG execution logic with Validation Guardrails."""
        
        # 1. Privacy & Scope Verification (Input Guardrails)
        passed, message = process_guardrails(query)
        if not passed:
            return message
            
        # 2. Semantic Search (Retriever)
        query_embedding = self.embedder.embed_text(query)
        results = self.vector_store.search(query_embedding, k=3)
        
        # Filtering irrelevant chunks
        relevant_chunks = []
        for r in results:
            if r["score"] < 1.4: 
                relevant_chunks.append(r["metadata"])
                
        # 3. LLM Generation (Phase 4: Output Guardrails)
        if self.llm:
            answer = self.llm.generate_response(query, relevant_chunks)
            
            # PHASE 4: Post-Generation Validation
            # A. Final PII Scan on output
            from core.intent.guardrails import PersonalDataGuard
            pg = PersonalDataGuard()
            leaked_pii, _ = pg.contains_pii(answer)
            if leaked_pii:
                return "Security Alert: Response blocked due to sensitive data detection. Retrying generation..."
            
            # B. Link Verification (White-listed official domains only)
            OFFICIAL_DOMAINS = ["tatamutualfund.com", "tataamc.com", "sebi.gov.in", "tata.com"]
            if "Last updated from sources:" in answer:
                url_part = answer.split("Last updated from sources:")[-1].strip()
                if not any(domain in url_part for domain in OFFICIAL_DOMAINS):
                    # If citation is suspicious, strip it and add general disclaimer
                    answer = answer.split("Last updated from sources:")[0].strip()
                    answer += "\n\nLast updated from sources: official Tata Mutual Fund website."
            
            return answer
        else:
            if not relevant_chunks:
                return "The requested information is not available in the current knowledge base."
            
            sources = list(set([c.get("source_url") for c in relevant_chunks]))
            return f"[TEST MODE] Found data in {len(relevant_chunks)} chunks from: {sources}. LLM would generate a concise reply based on this."

# Test Execution
if __name__ == "__main__":
    bot = TataMF_Chatbot()
    test_queries = [
        "What is the NAV of Tata Flexi Cap Fund?",
        "How can I download my account statements?",
        "Can you recommend the best scheme for me?",  # Should be blocked
        "My PAN number is ABCDE1234F, check my folio", # PII should be blocked
        "How has the fund performed vs Nifty 50?"     # Comparison should be redirected
    ]
    
    for q in test_queries:
        print(f"\nUser: {q}")
        print(f"Bot: {bot.ask(q)}")
