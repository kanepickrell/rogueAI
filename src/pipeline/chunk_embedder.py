from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

class DocumentEmbedder:
    def __init__(self, model_name='all-MiniLM-L6-v2', min_clusters=2, max_clusters=10):
        self.model = SentenceTransformer(model_name)
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.embeddings = None
        self.clusters = None
        self.kmeans = None
        self.pca = PCA(n_components=2)
        self.embeddings_2d = None
        self.chunks = None
        
    def create_embeddings(self, chunks):
        """Create embeddings from document chunks"""
        self.chunks = chunks
        texts = [chunk.text for chunk in chunks]
        # Ensure embeddings are float64
        self.embeddings = np.array(self.model.encode(texts), dtype=np.float64)
        self.embeddings_2d = self.pca.fit_transform(self.embeddings)
        return self.embeddings

    def cluster_documents(self):
      """Cluster documents using optimal number of clusters"""
      optimal_k = self.find_optimal_clusters()
      self.kmeans = KMeans(n_clusters=optimal_k, random_state=42)
      self.clusters = self.kmeans.fit_predict(self.embeddings)
      return self.clusters
        
    def find_optimal_clusters(self):
        """Find optimal number of clusters using silhouette analysis"""
        silhouette_scores = []
        
        for k in range(self.min_clusters, self.max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(self.embeddings)
            score = silhouette_score(self.embeddings, labels)
            silhouette_scores.append(score)
            
        optimal_k = np.argmax(silhouette_scores) + self.min_clusters
        return optimal_k
        
    def find_relevant_chunks(self, query, top_k=4):
        """Find and print most relevant chunks within query's cluster"""
        # Encode query and ensure dtype matches
        query_embedding = np.array(self.model.encode([query])[0], dtype=np.float64)
        query_cluster = self.kmeans.predict(query_embedding.reshape(1, -1))[0]
        
        print(f"\nQuery is in cluster {query_cluster}")
        print("-" * 80)
        
        # Get indices of chunks in same cluster
        cluster_mask = self.clusters == query_cluster
        cluster_indices = np.where(cluster_mask)[0]
        
        # Calculate similarities for chunks in same cluster
        cluster_embeddings = self.embeddings[cluster_mask]
        similarities = cosine_similarity([query_embedding], cluster_embeddings)[0]
        
        # Get top k similar chunks within cluster
        top_k = min(top_k, len(similarities))
        top_cluster_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Map back to original indices and print results
        top_indices = cluster_indices[top_cluster_indices]
        top_scores = similarities[top_cluster_indices]
        
        print(f"Top {top_k} matches in cluster {query_cluster}:")
        context = []
        for idx, score in zip(top_indices, top_scores):
            print("\nSimilarity Score:", f"{score:.4f}")
            print("Text:", self.chunks[idx].text)
            print("-" * 80)
            context.append(self.chunks[idx].text)
        
        return top_indices, top_scores, context
        
    def plot_embeddings(self, query=None, relevant_indices=None):
        """Plot document embeddings with optional query and relevant chunks"""
        plt.figure(figsize=(5, 4))
        
        scatter = plt.scatter(self.embeddings_2d[:, 0], self.embeddings_2d[:, 1],
                            c=self.clusters, cmap='viridis', alpha=0.6)
        
        if query is not None:
            query_embedding = np.array(self.model.encode([query]), dtype=np.float64)
            query_2d = self.pca.transform(query_embedding)
            query_cluster = self.kmeans.predict(query_embedding)[0]
            plt.scatter(query_2d[:, 0], query_2d[:, 1],
                      color='red', marker='*', s=200, 
                      label=f'Query (Cluster {query_cluster})')
        
        if relevant_indices is not None:
            retrieved_2d = self.embeddings_2d[relevant_indices]
            plt.scatter(retrieved_2d[:, 0], retrieved_2d[:, 1],
                      color='red', s=100, alpha=0.5, 
                      label=f'Top {len(relevant_indices)} in Cluster')
        
        plt.colorbar(scatter, label='Clusters')
        plt.title("Document Embeddings Visualization")
        plt.legend()
        plt.grid(True)
        return plt

    def process_chunks(self, chunks, query=None):
        """Process chunks and optionally find relevant ones for a query"""
        self.create_embeddings(chunks)
        self.cluster_documents()
        
        if query:
            # Updated to handle three return values
            top_indices, top_scores, context = self.find_relevant_chunks(query)
            self.plot_embeddings(query, top_indices)
            return top_indices, top_scores, context
        
        self.plot_embeddings()
        return None, None, None

    def get_cluster_info(self):
      """Get information about each cluster"""
      if self.kmeans is None or self.clusters is None:
          return {}
          
      cluster_info = {}
      unique_clusters = np.unique(self.clusters)
      
      for cluster_id in unique_clusters:
          mask = self.clusters == cluster_id
          cluster_info[cluster_id] = {
              'size': sum(mask),
              'chunks': [self.chunks[i].text for i in np.where(mask)[0]]
          }
      return cluster_info