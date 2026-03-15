import os
import sys

# Ensure indexing folder is in path
sys.path.append(os.getcwd())

from config import indexing_config
from indexing.embedders.hf_embedder import HFEmbedder
from indexing.vector_store.faiss_store import FAISSStore

def test_retrieval():
    query = "What is the exit load of Tata Flexi Cap Fund?"
    print(f"Testing retrieval for query: '{query}'")
    
    embedder = HFEmbedder(indexing_config.EMBEDDING_MODEL_NAME)
    vector_store = FAISSStore(dimension=384, index_path=indexing_config.VECTOR_DB_PATH)
    
    # Load the index
    vector_store.load_index(indexing_config.FAISS_INDEX_NAME)
    
    # Embed the query
    query_embedding = embedder.embed_text(query)
    
    # Search
    results = vector_store.search(query_embedding, k=3)
    
    print("\n--- Retrieval Results ---")
    for r in results:
        meta = r["metadata"]
        print(f"Fund: {meta.get('fund_name')}")
        print(f"Section: {meta.get('section')}")
        print(f"URL: {meta.get('source_url')}")
        print(f"Score: {r['score']:.4f}")
        print("-" * 30)

if __name__ == "__main__":
    test_retrieval()
