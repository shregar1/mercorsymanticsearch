import faiss
import numpy as np
import voyageai

from langchain.output_parsers import PydanticOutputParser
from typing import List, Dict, Any

from dtos.services.search.hard_criteria import HardCriteria
from constants.prompt import Prompt
from services.llm.generate import LLMGenerateService
from services.vector_store.abstraction import IVectorStoreService

from start_utils import logger


class SearchVectorStoreService(IVectorStoreService):
    """
    Service for reading embeddings from a FAISS index
    """

    def __init__(
        self,
        faiss_indices: Dict[int, Dict[str, Any]],
        profiles: List[Dict[str, Any]],
        embedding_model: voyageai.Client,
    ):
        """
        Initialize the vector store read service
        """
        super().__init__()
        self.logger = logger
        self.llm_generate_service = LLMGenerateService()
        self.faiss_indices = faiss_indices
        self.profiles = profiles
        self.embedding_model = embedding_model

    def search_in_clusters(
        self,
        query: str,
        top_k: int,
        relevant_clusters: List[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """
        Search for profiles using RAG with clustering
        """
        self.logger.info(f"Searching for: '{query}'")

        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding.astype('float32'))

        all_results = []

        for cluster_id in relevant_clusters:
            if cluster_id not in self.faiss_indices:
                continue

            cluster_info = self.faiss_indices[cluster_id]
            index = cluster_info['index']
            profile_indices = cluster_info['profile_indices']

            self.logger.info(f"Searching in cluster {cluster_id}")
            k_for_cluster = min(top_k * 3, len(profile_indices))
            similarities, faiss_indices = index.search(
                query_embedding.astype('float32'),
                k_for_cluster,
            )

            self.logger.info(
                f"Found {len(faiss_indices)} candidates in "
                f"cluster {cluster_id}",
            )
            faiss_to_profile_map = {}
            for faiss_idx, sim_score in zip(faiss_indices[0], similarities[0]):
                if faiss_idx < len(profile_indices):  # Valid FAISS index
                    actual_profile_idx = profile_indices[faiss_idx]
                    faiss_to_profile_map[actual_profile_idx] = float(sim_score)

            self.logger.info(
                f"Found {len(faiss_to_profile_map)} candidates in "
                f"cluster {cluster_id}",
            )
            candidate_profile_indices = list(faiss_to_profile_map.keys())

            parser = PydanticOutputParser(pydantic_object=HardCriteria)
            prompt = Prompt.HARD_CRITERIA_PROMPT.format(query)
            llm_response = self.llm_generate_service.run(
                prompt=prompt,
            )
            hard_criteria: HardCriteria = parser.parse(llm_response.content)

            if hard_criteria:
                filtered_indices = self.apply_hard_criteria(
                    np.array(candidate_profile_indices),
                    hard_criteria,
                )
                self.logger.info(
                    f"Cluster {cluster_id}: {len(candidate_profile_indices)} "
                    f"candidates -> {len(filtered_indices)} after filtering",
                )
            else:
                filtered_indices = candidate_profile_indices

            for profile_idx in filtered_indices:
                if profile_idx in faiss_to_profile_map:
                    result = {
                        'profile': self.profiles[profile_idx],
                        'similarity': faiss_to_profile_map[profile_idx],
                        'cluster_id': cluster_id
                    }
                    all_results.append(result)
        all_results.sort(key=lambda x: x['similarity'], reverse=True)
        return all_results[:top_k]

    def run(
        self,
        query: str,
        top_k: int = 10,
        relevant_clusters: List[np.ndarray] = None,
    ):
        """
        Search the vector store for the most similar embeddings to the query
        """
        return self.search_in_clusters(
            query=query,
            top_k=top_k,
            relevant_clusters=relevant_clusters,
        )
