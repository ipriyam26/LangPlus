"""Test PGVector functionality."""
import os
from typing import List

from sqlalchemy.orm import Session

from langplus.docstore.document import Document
from langplus.vectorstores.analyticdb import AnalyticDB
from tests.integration_tests.vectorstores.fake_embeddings import FakeEmbeddings

CONNECTION_STRING = AnalyticDB.connection_string_from_db_params(
    driver=os.environ.get("PG_DRIVER", "psycopg2cffi"),
    host=os.environ.get("PG_HOST", "localhost"),
    port=int(os.environ.get("PG_HOST", "5432")),
    database=os.environ.get("PG_DATABASE", "postgres"),
    user=os.environ.get("PG_USER", "postgres"),
    password=os.environ.get("PG_PASSWORD", "postgres"),
)


ADA_TOKEN_COUNT = 1536


class FakeEmbeddingsWithAdaDimension(FakeEmbeddings):
    """Fake embeddings functionality for testing."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return simple embeddings."""
        return [
            [float(1.0)] * (ADA_TOKEN_COUNT - 1) + [float(i)] for i in range(len(texts))
        ]

    def embed_query(self, text: str) -> List[float]:
        """Return simple embeddings."""
        return [float(1.0)] * (ADA_TOKEN_COUNT - 1) + [float(0.0)]


def test_analyticdb() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    docsearch = AnalyticDB.from_texts(
        texts=texts,
        collection_name="test_collection",
        embedding=FakeEmbeddingsWithAdaDimension(),
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo")]


def test_analyticdb_with_metadatas() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": str(i)} for i in range(len(texts))]
    docsearch = AnalyticDB.from_texts(
        texts=texts,
        collection_name="test_collection",
        embedding=FakeEmbeddingsWithAdaDimension(),
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo", metadata={"page": "0"})]


def test_analyticdb_with_metadatas_with_scores() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": str(i)} for i in range(len(texts))]
    docsearch = AnalyticDB.from_texts(
        texts=texts,
        collection_name="test_collection",
        embedding=FakeEmbeddingsWithAdaDimension(),
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search_with_score("foo", k=1)
    assert output == [(Document(page_content="foo", metadata={"page": "0"}), 0.0)]


def test_analyticdb_with_filter_match() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": str(i)} for i in range(len(texts))]
    docsearch = AnalyticDB.from_texts(
        texts=texts,
        collection_name="test_collection_filter",
        embedding=FakeEmbeddingsWithAdaDimension(),
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search_with_score("foo", k=1, filter={"page": "0"})
    assert output == [(Document(page_content="foo", metadata={"page": "0"}), 0.0)]


def test_analyticdb_with_filter_distant_match() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": str(i)} for i in range(len(texts))]
    docsearch = AnalyticDB.from_texts(
        texts=texts,
        collection_name="test_collection_filter",
        embedding=FakeEmbeddingsWithAdaDimension(),
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search_with_score("foo", k=1, filter={"page": "2"})
    print(output)
    assert output == [(Document(page_content="baz", metadata={"page": "2"}), 4.0)]


def test_analyticdb_with_filter_no_match() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": str(i)} for i in range(len(texts))]
    docsearch = AnalyticDB.from_texts(
        texts=texts,
        collection_name="test_collection_filter",
        embedding=FakeEmbeddingsWithAdaDimension(),
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search_with_score("foo", k=1, filter={"page": "5"})
    assert output == []


def test_analyticdb_collection_with_metadata() -> None:
    """Test end to end collection construction"""
    pgvector = AnalyticDB(
        collection_name="test_collection",
        collection_metadata={"foo": "bar"},
        embedding_function=FakeEmbeddingsWithAdaDimension(),
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    session = Session(pgvector.connect())
    collection = pgvector.get_collection(session)
    if collection is None:
        assert False, "Expected a CollectionStore object but received None"
    else:
        assert collection.name == "test_collection"
        assert collection.cmetadata == {"foo": "bar"}
