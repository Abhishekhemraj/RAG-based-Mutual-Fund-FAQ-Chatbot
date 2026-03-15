import os
from sentence_transformers import SentenceTransformer
import numpy as np

class HFEmbedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Use /tmp for model cache in serverless envs like Vercel
        cache_folder = "/tmp/transformers_cache" if os.getenv("VERCEL") == "1" else None
        self.model = SentenceTransformer(model_name, cache_folder=cache_folder)
    
    def embed_text(self, text):
        return self.model.encode(text)

    def embed_batch(self, texts):
        return self.model.encode(texts)
