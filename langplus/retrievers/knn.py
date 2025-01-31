"""KNN Retriever.
Largely based on
https://github.com/karpathy/randomfun/blob/master/knn_vs_svm.ipynb"""

from __future__ import annotations

import concurrent.futures
from typing import Any, List, Optional

import numpy as np
from pydantic import BaseModel

from langplus.embeddings.base import Embeddings
from langplus.schema import BaseRetriever, Document


def create_index(contexts: List[str], embeddings: Embeddings) -> np.ndarray:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return np.array(list(executor.map(embeddings.embed_query, contexts)))


class KNNRetriever(BaseRetriever, BaseModel):
    embeddings: Embeddings
    index: Any
    texts: List[str]
    k: int = 4
    relevancy_threshold: Optional[float] = None

    class Config:

        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @classmethod
    def from_texts(
        cls, texts: List[str], embeddings: Embeddings, **kwargs: Any
    ) -> KNNRetriever:
        index = create_index(texts, embeddings)
        return cls(embeddings=embeddings, index=index, texts=texts, **kwargs)

    def get_relevant_documents(self, query: str) -> List[Document]:
        query_embeds = np.array(self.embeddings.embed_query(query))
        # calc L2 norm
        index_embeds = self.index / np.sqrt((self.index**2).sum(1, keepdims=True))
        query_embeds = query_embeds / np.sqrt((query_embeds**2).sum())

        similarities = index_embeds.dot(query_embeds)
        sorted_ix = np.argsort(-similarities)

        denominator = np.max(similarities) - np.min(similarities) + 1e-6
        normalized_similarities = (similarities - np.min(similarities)) / denominator

        top_k_results = [
            Document(page_content=self.texts[row])
            for row in sorted_ix[0 : self.k]
            if (
                self.relevancy_threshold is None
                or normalized_similarities[row] >= self.relevancy_threshold
            )
        ]
        return top_k_results

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        raise NotImplementedError
