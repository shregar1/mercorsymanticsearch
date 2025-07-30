import numpy as np

from collections import defaultdict
from typing import Optional, List, Dict, Any

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


from start_utils import logger
from services.clustering.abstraction import IClusteringService


class KMeansClusteringService(IClusteringService):
    """
    KMeans clustering service
    """
    def __init__(self, n_clusters: Optional[int] = None):
        """
        Initialize the KMeans clustering service
        """
        super().__init__()
        self.logger = logger
        self.n_clusters = n_clusters

    def find_optimal_clusters(
        self,
        embeddings: np.ndarray,
        max_k: int = 100,
    ) -> int:
        """
        Find optimal number of clusters using elbow method and silhouette score
        """
        self.logger.info("Finding optimal number of clusters...")

        # For large datasets, use a subset for cluster optimization
        if len(embeddings) > 100000:
            sample_size = min(100000, len(embeddings))
            sample_indices = np.random.choice(
                len(embeddings),
                sample_size,
                replace=False,
            )
            print(sample_indices)
            sample_embeddings = embeddings[sample_indices]
        else:
            sample_embeddings = embeddings

        silhouette_scores = []
        inertias = []
        k_range = range(5, min(max_k, len(sample_embeddings) // 10))

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(sample_embeddings)

            silhouette_avg = silhouette_score(
                sample_embeddings,
                cluster_labels,
            )
            silhouette_scores.append(silhouette_avg)
            inertias.append(kmeans.inertia_)

            self.logger.info(f"k={k}, silhouette_score={silhouette_avg:.3f}")

        # Find optimal k using silhouette score
        optimal_k = k_range[np.argmax(silhouette_scores)]
        self.logger.info(f"Optimal number of clusters: {optimal_k}")

        return optimal_k

    def analyze_clusters(
        self,
        cluster_labels: np.ndarray,
        profiles: List[Dict[str, Any]],
    ):
        """
        Analyze cluster characteristics
        """
        self.logger.info("\nCluster Analysis:")
        self.logger.info("-" * 50)

        for cluster_id in np.unique(cluster_labels):
            cluster_mask = cluster_labels == cluster_id
            cluster_profiles = [
                profiles[i] for i in np.where(cluster_mask)[0]
            ]

            industries = defaultdict(int)
            companies = defaultdict(int)
            skills = defaultdict(int)
            locations = defaultdict(int)
            avg_experience = np.mean(
                [p.experience_years for p in cluster_profiles],
            )

            for profile in cluster_profiles:
                industries[profile.industry] += 1
                companies[profile.company] += 1
                locations[profile.location] += 1
                for skill in profile.skills:
                    if skill.strip():
                        skills[skill.strip().lower()] += 1

            self.cluster_metadata[cluster_id] = {
                'size': len(cluster_profiles),
                'avg_experience': avg_experience,
                'top_industries': dict(
                    sorted(
                        industries.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:5],
                ),
                'top_companies': dict(
                    sorted(
                        companies.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:5],
                ),
                'top_skills': dict(
                    sorted(
                        skills.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:10],
                ),
                'top_locations': dict(
                    sorted(
                        locations.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:5],
                ),
            }

            self.logger.info(
                f"\nCluster {cluster_id} ({len(cluster_profiles)} profiles):",
            )
            self.logger.info(
                f"  Avg Experience: {avg_experience:.1f} years",
            )
            self.logger.info(
                f"  Top Industries: {list(industries.keys())[:3]}",
            )
            self.logger.info(
                f"  Top Skills: {list(skills.keys())[:5]}",
            )

    def run(
        self,
        embeddings: np.ndarray,
    ) -> np.ndarray:
        """
        Create clusters using K-means
        """
        if self.n_clusters is None:
            self.n_clusters = self.find_optimal_clusters(embeddings)

        self.logger.info(f"Creating {self.n_clusters} clusters...")
        kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10,
        )
        cluster_labels = kmeans.fit(embeddings)

        self.cluster_centers = kmeans.cluster_centers_

        return cluster_labels.labels_, self.cluster_centers
