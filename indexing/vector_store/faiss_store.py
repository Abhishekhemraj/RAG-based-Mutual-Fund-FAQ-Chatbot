import os
import pickle
import numpy as np
import faiss

class FAISSStore:
    def __init__(self, dimension=384, index_path="data/vector_index"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
        
        if not os.path.exists(index_path):
            os.makedirs(index_path, exist_ok=True)

    def add_to_index(self, embeddings, metadata_list):
        embeddings = np.array(embeddings).astype('float32')
        self.index.add(embeddings)
        self.metadata.extend(metadata_list)

    def save_index(self, filename="tata_mf_index"):
        faiss.write_index(self.index, os.path.join(self.index_path, f"{filename}.faiss"))
        with open(os.path.join(self.index_path, f"{filename}_metadata.pickle"), "wb") as f:
            pickle.dump(self.metadata, f)

    def load_index(self, filename="tata_mf_index"):
        self.index = faiss.read_index(os.path.join(self.index_path, f"{filename}.faiss"))
        with open(os.path.join(self.index_path, f"{filename}_metadata.pickle"), "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, query_embedding, k=3):
        query_embedding = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:
                results.append({
                    "metadata": self.metadata[idx],
                    "score": float(distances[0][i])
                })
        return results
