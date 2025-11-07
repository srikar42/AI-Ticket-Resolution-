import os
import pickle
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


class KnowledgeBaseIndexer:
    """
    A class to build and manage FAISS-based semantic search indexes
    for a knowledge base of support articles.
    """

    def __init__(self, 
                 data_path="data/raw/knowledge_base_articles2.csv",
                 model_name="all-MiniLM-L6-v2",
                 output_dir="models"):
        self.data_path = data_path
        self.model_name = model_name
        self.output_dir = output_dir
        self.articles = None
        self.embeds = None
        self.index = None
        self.model = None

        os.makedirs(self.output_dir, exist_ok = True)

    def load_data(self):
        """Load article data from CSV and prepare text field."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        self.articles = pd.read_csv(self.data_path, encoding='ISO-8859-1')
        
        if not {"title", "body"}.issubset(self.articles.columns):
            raise ValueError("CSV must contain 'title' and 'body' columns.")

        self.articles["text"] = self.articles["title"] + " " + self.articles["body"]
        print(f"Loaded {len(self.articles)} articles.")
    
    def load_model(self):
        """Load SentenceTransformer model."""
        self.model = SentenceTransformer(self.model_name)
    
    def compute_embeddings(self, normalize=True):
        """Generate embeddings for articles using SentenceTransformer."""
        if self.articles is None:
            raise ValueError("Articles not loaded. Run load_data() first.")
        if self.model is None:
            self.load_model()

        texts = self.articles["text"].tolist()
        self.embeds = self.model.encode(texts, convert_to_numpy=True)

        if normalize:
            faiss.normalize_L2(self.embeds)
    
    def build_index(self):
        """Build FAISS inner product index."""
        if self.embeds is None:
            raise ValueError("Embeddings not computed. Run compute_embeddings() first.")

        dim = self.embeds.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeds)
        print(f"FAISS index built with {self.index.ntotal} entries.")
    
    def save_index(self):
        """Save FAISS index, metadata, and model info."""
        if self.index is None or self.articles is None:
            raise ValueError("Index or articles missing. Run build_index() first.")
        
        index_path = os.path.join(self.output_dir, "article_index.faiss")
        meta_path = os.path.join(self.output_dir, "articles_meta.pkl")
        model_info_path = os.path.join(self.output_dir, "embed_model.pkl")

        faiss.write_index(self.index, index_path)
        self.articles.to_pickle(meta_path)
        with open(model_info_path, "wb") as f:
            pickle.dump({"model_name": self.model_name}, f)

        print(f"Saved index and metadata in '{self.output_dir}'")
        print(f" - Index: {index_path}")
        print(f" - Metadata: {meta_path}")
        print(f" - Model info: {model_info_path}")

    def run_full_pipeline(self):
        """Run the full indexing pipeline: load → encode → build → save."""
        self.load_data()
        self.load_model()
        self.compute_embeddings()
        self.build_index()
        self.save_index()


# Example usage
if __name__ == "__main__":
    indexer = KnowledgeBaseIndexer()
    indexer.run_full_pipeline()
