import os

# Embedding Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Vector DB Configuration
VECTOR_DB_PATH = "data/vector_index"
FAISS_INDEX_NAME = "tata_mf_index"

# Chunking Strategy (used during ingestion)
CHUNK_SIZE = 800
CHUNK_OVERLAP = 80

# Source White-list
OFFICIAL_DOMAINS = [
    "tatamutualfund.com",
    "indmoney.com",
    "camsonline.com",
    "sebi.gov.in"
]
