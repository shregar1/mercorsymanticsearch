# Fixed VectorStoreWriteService class
import numpy as np
import faiss
from typing import List
from services.vector_store.abstraction import IVectorStoreService
from start_utils import logger

class VectorStoreWriteService(IVectorStoreService):
    """
    Service for writing embeddings to vector store with clustering support.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logger
    
    def write(self, embeddings: np.ndarray, cluster_labels: np.ndarray, target_cluster_label: int):
        """
        Write embeddings for a specific cluster to the vector store.
        
        Args:
            embeddings: Array of all embeddings
            cluster_labels: Array of cluster labels for all embeddings
            target_cluster_label: The specific cluster label to filter for
        """
        # Create boolean mask for the target cluster
        cluster_mask = cluster_labels == target_cluster_label
        cluster_embeddings = embeddings[cluster_mask]
        cluster_profile_indices = np.where(cluster_mask)[0]
        
        self.logger.info(
            f"Cluster {target_cluster_label}: {len(cluster_embeddings)} profiles, "
            f"{len(cluster_profile_indices)} profile indices"
        )
        
        # Get the dimension of embeddings
        dimension = cluster_embeddings.shape[1]
        
        # Create index for the cluster
        index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings to the index
        index.add(cluster_embeddings.astype('float32'))
        
        # Save the index
        faiss.write_index(index, f"cluster_{target_cluster_label}.index")
        
        # Save the profile indices
        np.save(f"cluster_{target_cluster_label}_indices.npy", cluster_profile_indices)
        
        self.logger.info(f"Saved cluster {target_cluster_label} with {len(cluster_embeddings)} embeddings")
    
    def run(self, embeddings: np.ndarray, cluster_labels: np.ndarray):
        """
        Write embeddings for all clusters to the vector store.
        
        Args:
            embeddings: Array of all embeddings
            cluster_labels: Array of cluster labels for all embeddings
        """
        self.logger.info(f"Writing embeddings for {len(embeddings)} profiles with clustering")
        
        # Get unique cluster labels
        unique_clusters = np.unique(cluster_labels)
        
        for cluster_label in unique_clusters:
            self.logger.info(f"Writing embeddings for cluster {cluster_label}")
            self.write(embeddings, cluster_labels, cluster_label)
            self.logger.info(f"Written embeddings for cluster {cluster_label}")
        
        self.logger.info("Vector store write service completed")

# Usage example:
# vector_store_write_service = VectorStoreWriteService()
# vector_store_write_service.run(
#     embeddings=np.array(embeddings),
#     cluster_labels=kmean_cluster_labels,
# )
