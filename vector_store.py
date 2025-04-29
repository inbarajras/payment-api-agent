import json
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

class VectorStore:
    def __init__(self, embeddings_file):
        # Load embeddings
        with open(embeddings_file, 'r') as f:
            data = json.load(f)

        self.documents = data
        self.embeddings = np.array([item['embedding'] for item in data])
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, query, top_k=5):
        # Encode query
        query_embedding = self.model.encode(query)

        # Calculate distances
        distances = [1 - cosine(query_embedding, doc_embedding) for doc_embedding in self.embeddings]

        # Get top results
        top_indices = np.argsort(distances)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            doc = self.documents[idx].copy()
            doc['relevance_score'] = float(distances[idx])
            # Remove the embedding to make output cleaner
            doc.pop('embedding')
            results.append(doc)

        return results

# Create vector stores
paypal_store = VectorStore("vector_db/paypal/embeddings.json")
stripe_store = VectorStore("vector_db/stripe/embeddings.json")

# Example search
results = paypal_store.search("How do I process a payment?")
print(json.dumps(results[:2], indent=2))

