"""Test the cohere reranker."""

from langplus.retrievers.document_compressors.cohere_rerank import CohereRerank


def test_cohere_reranker_init() -> None:
    """Test the cohere reranker initializes correctly."""
    CohereRerank()
