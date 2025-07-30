import aiohttp
import asyncio
import json
import numpy as np
import os
import tqdm


from typing import List, Optional, Dict
from voyageai.object.embeddings import EmbeddingsObject

from services.vector_store.abstraction import IVectorStoreService

from start_utils import voyageai_client, logger, VOYAGEAI_API_KEY


class VectorStoreEmbeddingService(IVectorStoreService):
    """
    Service for generating embeddings using a specified model (Voyage or
    OpenAI). Provides methods for single and batch embedding, and model
    loading.
    """

    def __init__(
        self,
        model_name: str,
        max_concurrent_requests: int = 10,
        use_progress: bool = True,
        save_embeddings: bool = True,
        embeddings_dir: str = "embeddings",
    ):
        """
        Initialize the embedding service with a model name.
        Args:
            model_name (str): The name of the embedding model to use.
            max_concurrent_requests (int): Maximum number of concurrent
            requests.
            use_progress (bool): Whether to show progress bar by default.
            save_embeddings (bool): Whether to save embeddings to JSON file.
            embeddings_file (str): Path to save embeddings JSON file.
        """
        super().__init__()
        self.model_name = model_name
        self.model = voyageai_client
        self.logger = logger
        self.max_concurrent_requests = max_concurrent_requests
        self.use_progress = use_progress
        self.save_embeddings = save_embeddings
        self.embeddings_dir = embeddings_dir
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.logger.info(
            f"Initialized VectorStoreEmbeddingService with max "
            f"{max_concurrent_requests} concurrent requests"
        )

    async def embed(self, text: str):
        """
        Generate an embedding for a single text string.
        Args:
            text (str): The input text to embed.
        Returns:
            The embedding vector or None if embedding fails.
        """
        self.logger.info(f"Embedding text: {text}")
        try:
            embedding_response: EmbeddingsObject = self.model.embed(
                model=self.model_name,
                texts=[text],
            )
            embedding = embedding_response.embeddings[0]
            if not embedding:
                return None
            return embedding
        except Exception as e:
            self.logger.error(f"Error in embed: {e}")
            return None

    async def embed_with_aiohttp(
        self,
        session: aiohttp.ClientSession,
        key: str,
        text: str,
    ) -> Optional[List[float]]:
        """
        Generate an embedding for a single text using aiohttp.
        Args:
            session (aiohttp.ClientSession): The HTTP session to use.
            text (str): The input text to embed.
        Returns:
            The embedding vector or None if embedding fails.
        """
        async with self.semaphore:
            try:
                url = "https://api.voyageai.com/v1/embeddings"
                headers = {
                    "Authorization": f"Bearer {VOYAGEAI_API_KEY}",
                    "Content-Type": "application/json",
                }
                payload = {"model": self.model_name, "input": [text]}

                async with session.post(
                    url, headers=headers, json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data") and len(data["data"]) > 0:
                            return {
                                "key": key,
                                "embedding": (
                                    np.array(
                                        data.get(
                                            "data", [{}],
                                        )[0].get("embedding"),
                                        dtype=np.float32,
                                    ),
                                ),
                            }
                    else:
                        error_text = await response.text()
                        self.logger.error(
                            f"HTTP {response.status}: {error_text}"
                        )
                    return None
            except Exception as e:
                self.logger.error(
                    f"Error embedding text '{text[:50]}...': {e}"
                )
                return None

    async def embed_batch_async(
        self,
        texts: List[tuple],
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts concurrently using aiohttp.
        Args:
            texts (List[str]): List of input texts to embed.
        Returns:
            List of embedding vectors (None for failed embeddings).
        """
        if not texts:
            return []

        connector = aiohttp.TCPConnector(ssl=False)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for key, text in texts:
                task = self.embed_with_aiohttp(session, key, text)
                tasks.append(task)

            # Use asyncio.gather to run all tasks concurrently
            embeddings = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions that occurred
            processed_embeddings = []
            for i, result in enumerate(embeddings):
                if isinstance(result, Exception):
                    self.logger.error(f"Exception for text {i}: {result}")
                    processed_embeddings.append(None)
                else:
                    processed_embeddings.append(result)

            return processed_embeddings

    def save_embeddings_to_json(
        self,
        embeddings_file: str,
        embeddings: List[Optional[dict]]
    ) -> None:
        """
        Save embeddings to JSON file after each batch.
        Args:
            texts (List[str]): List of input texts.
            embeddings (List[Optional[List[float]]]): List of embeddings.
            batch_index (int): Current batch index for tracking.
        """
        if not self.save_embeddings:
            return

        try:

            with open(embeddings_file, "w", encoding="utf-8") as f:
                json.dump(embeddings, f)

        except Exception as e:
            self.logger.error(f"Error saving embeddings to JSON: {e}")

    async def embed_batch_with_progress(
        self, texts: List[str]
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts with progress tracking.
        Args:
            texts (List[str]): List of input texts to embed.
        Returns:
            List of embedding vectors (None for failed embeddings).
        """
        if not texts:
            return []

        with tqdm.tqdm(total=len(texts), desc="Embedding texts") as pbar:
            for batch_idx, i in enumerate(
                range(0, len(texts), self.max_concurrent_requests)
            ):
                chunk = texts[i: i + self.max_concurrent_requests]
                chunk_embeddings = await self.embed_batch_async(chunk)

                self.save_embeddings_to_json(
                    os.path.join(
                        self.embeddings_dir,
                        f"batch_v2_{194+batch_idx}.json",
                    ),
                    chunk_embeddings,
                )

                pbar.update(len(chunk))
        return None

    def run(self, texts: List[str]):
        """
        Synchronous embedding generation for a single text string.
        Args:
            texts (List[str]): List of input texts to embed.
        Returns:
            List of embedding vectors or None if embedding fails.
        """
        try:
            self.logger.info(f"Embedding {len(texts)} texts...")
            embeddings = []
            for text in tqdm.tqdm(texts):
                embedding = self.embed(text)
                if embedding:
                    embeddings.append(embedding)
            self.logger.info(f"Embedded {len(embeddings)} texts...")
            return embeddings
        except Exception as e:
            self.logger.error(f"Error in run: {e}")
            return None

    async def run_async(
        self,
        texts: Dict[str, str],
        use_progress: Optional[bool] = True
    ) -> List[Optional[List[float]]]:
        """
        Asynchronous embedding generation for multiple texts.
        Args:
            texts (List[str]): List of input texts to embed.
            use_progress (Optional[bool]): Whether to show progress bar.
                If None, uses the default setting from initialization.
        Returns:
            List of embedding vectors (None for failed embeddings).
        """
        try:
            # Use instance default if not specified
            if use_progress is None:
                use_progress = self.use_progress

            texts = list(texts.items())
            if use_progress:
                return await self.embed_batch_with_progress(texts)
            else:
                return await self.embed_batch_async(texts)
        except Exception as e:
            self.logger.error(f"Error in run_async: {e}")
            return []
