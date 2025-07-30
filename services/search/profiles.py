import faiss

import numpy as np
from typing import List, Dict, Any, Optional

from dtos.services.etl.profile import ProfileData
from dtos.services.search.hard_criteria import HardCriteria

from services.search.abstraction import ISearchService

from start_utils import logger


class SearchProfilesService(ISearchService):
    """
    Service for searching for profiles
    """

    def __init__(
        self,
        profiles: List[ProfileData],
        faiss_indices: Dict[int, Dict[str, Any]],
        cluster_centers: np.ndarray,
        cluster_labels: np.ndarray,
        embedding_model,
        model_name: str,
    ):
        """
        Initialize the hard criteria search service
        """
        super().__init__()
        self.logger = logger
        self.profiles = profiles
        self.model_name = model_name
        self.faiss_indices = faiss_indices
        self.cluster_centers = cluster_centers
        self.cluster_labels = cluster_labels
        self.embedding_model = embedding_model

    def apply_hard_criteria(
        self,
        profile_indices: np.ndarray,
        criteria: HardCriteria,
    ) -> np.ndarray:
        """
        Apply hard criteria filtering to profile indices with lenient matching.
        For each category (skills, locations, industries, companies,
        education),
        if multiple criteria are provided, only ONE needs to be met.
        """
        valid_indices = []

        for idx in profile_indices:
            profile: ProfileData = self.profiles[idx]

            # Check experience range (this remains strict - must meet min/max
            # requirements)
            self.logger.info(f"Checking experience range for profile {idx}")
            if (
                criteria.min_experience is not None
                and profile.experience_years < criteria.min_experience
            ):
                continue

            if (
                criteria.max_experience is not None
                and profile.experience_years > criteria.max_experience
            ):
                continue

            # Check required skills (lenient - only ONE skill needs to match)
            self.logger.info(f"Checking required skills for profile {idx}")
            if criteria.required_skills:
                profile_skills_lower = [
                    skill.lower().strip() for skill in profile.skills
                ]
                required_skills_lower = [
                    skill.lower().strip() for skill in criteria.required_skills
                ]
                # Changed from all() to any() - only one skill needs to match
                if not any(
                    req_skill in profile_skills_lower
                    for req_skill in required_skills_lower
                ):
                    continue

            # Check excluded skills (remains strict - any excluded skill
            # disqualifies)
            self.logger.info(f"Checking excluded skills for profile {idx}")
            if criteria.excluded_skills:
                profile_skills_lower = [
                    skill.lower().strip() for skill in profile.skills
                ]
                excluded_skills_lower = [
                    skill.lower().strip() for skill in criteria.excluded_skills
                ]
                if any(
                    exc_skill in profile_skills_lower
                    for exc_skill in excluded_skills_lower
                ):
                    continue

            # Check locations (lenient - only ONE location needs to match)
            self.logger.info(f"Checking locations for profile {idx}")
            profile_locations = {
                ws_locations.lower()
                for ws_locations in (
                    profile.work_locations + profile.study_locations
                )
            }
            if criteria.locations:
                if not any(
                    loc.lower() in profile_locations
                    for loc in criteria.locations
                ):
                    continue

            # Check industries (lenient - only ONE industry needs to match)
            self.logger.info(f"Checking industries for profile {idx}")
            if criteria.industries:
                if not any(
                    ind.lower() in profile.industry.lower()
                    for ind in criteria.industries
                ):
                    continue

            # Check companies (lenient - only ONE company needs to match)
            self.logger.info(f"Checking companies for profile {idx}")
            if criteria.companies:
                if not any(
                    comp.lower() in profile.company.lower()
                    for comp in criteria.companies
                ):
                    continue

            # Check education keywords (lenient - only ONE keyword needs to
            # match)
            self.logger.info(f"Checking education keywords for profile {idx}")
            if criteria.education_keywords:
                if not any(
                    keyword.lower() in profile.education.lower()
                    for keyword in criteria.education_keywords
                ):
                    continue

            valid_indices.append(idx)

        return np.array(valid_indices)

    def find_relevant_clusters(
        self,
        query: str,
        top_k_clusters: int = 5,
    ) -> List[int]:
        """
        Find most relevant clusters for a query
        """
        # Create embedding for query
        query_embedding = self.embedding_model.embed(
            model=self.model_name,
            texts=[query],
        )
        query_embedding = np.array(
            query_embedding.embeddings[0],
            dtype=np.float32,
        ).reshape(1, -1)
        faiss.normalize_L2(query_embedding)

        # Calculate similarity with cluster centers
        cluster_similarities = []
        normalized_centers = self.cluster_centers.copy().astype("float32")
        faiss.normalize_L2(normalized_centers)

        for cluster_id, center in enumerate(normalized_centers):
            similarity = np.dot(query_embedding[0], center)
            cluster_similarities.append((cluster_id, similarity))

        # Sort by similarity and return top k clusters
        cluster_similarities.sort(key=lambda x: x[1], reverse=True)
        relevant_clusters = [
            cluster_id
            for cluster_id, _ in cluster_similarities[:top_k_clusters]
            if cluster_id in self.faiss_indices
        ]
        self.logger.info(f"Selected clusters for query: {relevant_clusters}")
        return relevant_clusters

    def search(
        self,
        query: str,
        hard_criteria: Optional[HardCriteria] = None,
        top_k: int = 10,
        top_k_clusters: int = 3,
    ) -> List[ProfileData]:
        """
        Search for profiles using RAG with clustering and hard criteria
        """
        print(f"\nSearching for: '{query}'")

        # Find relevant clusters
        relevant_clusters = self.find_relevant_clusters(query, top_k_clusters)

        # Create query embedding
        query_embedding = self.embedding_model.embed(
            model=self.model_name,
            texts=[query],
        )
        query_embedding = np.array(
            query_embedding.embeddings[0],
            dtype=np.float32,
        ).reshape(1, -1)
        faiss.normalize_L2(query_embedding)

        all_results = []

        for cluster_id in relevant_clusters:
            if cluster_id not in self.faiss_indices:
                continue

            cluster_info = self.faiss_indices[cluster_id]
            index = cluster_info["index"]
            profile_indices = cluster_info["profile_indices"]

            # Search in cluster
            k_for_cluster = min(
                top_k * 3, len(profile_indices)
            )  # Get more candidates for filtering
            similarities, faiss_indices = index.search(
                query_embedding.astype("float32"), k_for_cluster
            )

            # Create mapping from FAISS index to actual profile index and
            # similarity
            faiss_to_profile_map = {}
            for faiss_idx, sim_score in zip(faiss_indices[0], similarities[0]):
                if faiss_idx < len(profile_indices):  # Valid FAISS index
                    actual_profile_idx = profile_indices[faiss_idx]
                    faiss_to_profile_map[actual_profile_idx] = float(sim_score)

            # Get all candidate profile indices
            candidate_profile_indices = list(faiss_to_profile_map.keys())

            # Apply hard criteria filtering
            if hard_criteria:
                filtered_indices = self.apply_hard_criteria(
                    np.array(candidate_profile_indices), hard_criteria
                )
                print(
                    f"Cluster {cluster_id}: {len(candidate_profile_indices)} "
                    f"candidates -> {len(filtered_indices)} after filtering"
                )
            else:
                filtered_indices = candidate_profile_indices

            # Collect results with similarity scores
            for profile_idx in filtered_indices:
                if profile_idx in faiss_to_profile_map:
                    result = {
                        "profile": self.profiles[profile_idx],
                        "similarity": faiss_to_profile_map[profile_idx],
                        "cluster_id": cluster_id,
                    }
                    all_results.append(result)

        # Sort all results by similarity and return top k
        all_results.sort(key=lambda x: x["similarity"], reverse=True)
        return all_results[:top_k]

    def run(
        self,
        query: str,
        hard_criteria: Optional[HardCriteria] = None,
        top_k: int = 5,
        top_k_clusters: int = 5,
    ) -> List[ProfileData]:
        """
        Search for profiles using hard criteria
        """

        return self.search(
            query=query,
            hard_criteria=hard_criteria,
            top_k=top_k,
            top_k_clusters=top_k_clusters,
        )
