import os
import json
import sys

# Ensure indexing folder is in path
sys.path.append(os.getcwd())

from config import indexing_config
from indexing.embedders.hf_embedder import HFEmbedder
from indexing.vector_store.faiss_store import FAISSStore

def build_index():
    cleaned_dir = "data/cleaned"
    embedder = HFEmbedder(indexing_config.EMBEDDING_MODEL_NAME)
    vector_store = FAISSStore(dimension=384, index_path=indexing_config.VECTOR_DB_PATH)
    
    metadata_list = []
    text_contents = []
    
    if not os.path.exists(cleaned_dir):
        print(f"Cleaned directory {cleaned_dir} does not exist.")
        return

    for filename in os.listdir(cleaned_dir):
        if filename.endswith(".json"):
            with open(os.path.join(cleaned_dir, filename), "r", encoding="utf-8") as f:
                chunks = json.load(f)
                for chunk in chunks:
                    text_contents.append(chunk["content"])
                    # Save EVERY field including 'content' as metadata for RAG grounding
                    metadata_list.append(chunk)
    
    if text_contents:
        print(f"Beginning embedding process for {len(text_contents)} chunks...")
        embeddings = embedder.embed_batch(text_contents)
        vector_store.add_to_index(embeddings, metadata_list)
        vector_store.save_index(indexing_config.FAISS_INDEX_NAME)
        print(f"Index built successfully at {indexing_config.VECTOR_DB_PATH}")
    else:
        print("No cleaned data found in data/cleaned.")

if __name__ == "__main__":
    build_index()
