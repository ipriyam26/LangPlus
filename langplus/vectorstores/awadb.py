"""Wrapper around AwaDB for embedding vectors"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Tuple, Type

from langplus.docstore.document import Document
from langplus.embeddings.base import Embeddings
from langplus.vectorstores.base import VectorStore

# from pydantic import BaseModel, Field, root_validator


if TYPE_CHECKING:
    import awadb

logger = logging.getLogger()
DEFAULT_TOPN = 4


class AwaDB(VectorStore):
    """Interface implemented by AwaDB vector stores."""

    _DEFAULT_TABLE_NAME = "langchain_awadb"

    def __init__(
        self,
        table_name: str = _DEFAULT_TABLE_NAME,
        embedding_model: Optional[Embeddings] = None,
        log_and_data_dir: Optional[str] = None,
        client: Optional[awadb.Client] = None,
    ) -> None:
        """Initialize with AwaDB client."""

        try:
            import awadb
        except ImportError:
            raise ValueError(
                "Could not import awadb python package. "
                "Please install it with `pip install awadb`."
            )

        if client is not None:
            self.awadb_client = client
        else:
            if log_and_data_dir is not None:
                self.awadb_client = awadb.Client(log_and_data_dir)
            else:
                self.awadb_client = awadb.Client()

        self.awadb_client.Create(table_name)
        if embedding_model is not None:
            self.embedding_model = embedding_model

        self.added_doc_count = 0

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Run more texts through the embeddings and add to the vectorstore.
        Args:
            texts: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        if self.awadb_client is None:
            raise ValueError("AwaDB client is None!!!")

        embeddings = None
        if self.embedding_model is not None:
            embeddings = self.embedding_model.embed_documents(list(texts))
        added_results: List[str] = []
        doc_no = 0
        for text in texts:
            doc: List[Any] = []
            if embeddings is not None:
                doc.append(text)
                doc.append(embeddings[doc_no])
            else:
                dict_tmp = {}
                dict_tmp["embedding_text"] = text
                doc.append(dict_tmp)

            if metadatas is not None:
                if doc_no < metadatas.__len__():
                    doc.append(metadatas[doc_no])
            self.awadb_client.Add(doc)
            added_results.append(str(self.added_doc_count))

            doc_no = doc_no + 1
            self.added_doc_count = self.added_doc_count + 1

        return added_results

    def load_local(
        self,
        table_name: str = _DEFAULT_TABLE_NAME,
        **kwargs: Any,
    ) -> bool:
        if self.awadb_client is None:
            raise ValueError("AwaDB client is None!!!")

        return self.awadb_client.Load(table_name)

    def similarity_search(
        self,
        query: str,
        k: int = DEFAULT_TOPN,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs most similar to query."""
        if self.awadb_client is None:
            raise ValueError("AwaDB client is None!!!")

        embedding = None
        if self.embedding_model is not None:
            embedding = self.embedding_model.embed_query(query)

        return self.similarity_search_by_vector(embedding, k)

    def similarity_search_with_score(
        self,
        query: str,
        k: int = DEFAULT_TOPN,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Return docs and relevance scores, normalized on a scale from 0 to 1.

        0 is dissimilar, 1 is most similar.
        """

        if self.awadb_client is None:
            raise ValueError("AwaDB client is None!!!")

        embedding = None
        if self.embedding_model is not None:
            embedding = self.embedding_model.embed_query(query)

        show_results = self.awadb_client.Search(embedding, k)

        results: List[Tuple[Document, float]] = []

        if show_results.__len__() == 0:
            return results

        scores: List[float] = []
        retrieval_docs = self.similarity_search_by_vector(embedding, k, scores)

        L2_Norm = 0.0
        for score in scores:
            L2_Norm = L2_Norm + score * score

        L2_Norm = pow(L2_Norm, 0.5)
        doc_no = 0
        for doc in retrieval_docs:
            doc_tuple = (doc, 1 - scores[doc_no] / L2_Norm)
            results.append(doc_tuple)
            doc_no = doc_no + 1

        return results

    def similarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = DEFAULT_TOPN,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Return docs and relevance scores, normalized on a scale from 0 to 1.

        0 is dissimilar, 1 is most similar.
        """

        if self.awadb_client is None:
            raise ValueError("AwaDB client is None!!!")

        embedding = None
        if self.embedding_model is not None:
            embedding = self.embedding_model.embed_query(query)

        show_results = self.awadb_client.Search(embedding, k)

        results: List[Tuple[Document, float]] = []

        if show_results.__len__() == 0:
            return results

        scores: List[float] = []
        retrieval_docs = self.similarity_search_by_vector(embedding, k, scores)

        L2_Norm = 0.0
        for score in scores:
            L2_Norm = L2_Norm + score * score

        L2_Norm = pow(L2_Norm, 0.5)
        doc_no = 0
        for doc in retrieval_docs:
            doc_tuple = (doc, 1 - scores[doc_no] / L2_Norm)
            results.append(doc_tuple)
            doc_no = doc_no + 1

        return results

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = DEFAULT_TOPN,
        scores: Optional[list] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs most similar to embedding vector.

        Args:
            embedding: Embedding to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.

        Returns:
            List of Documents most similar to the query vector.
        """

        if self.awadb_client is None:
            raise ValueError("AwaDB client is None!!!")

        show_results = self.awadb_client.Search(embedding, k)

        results: List[Document] = []

        if show_results.__len__() == 0:
            return results

        for item_detail in show_results[0]["ResultItems"]:
            content = ""
            meta_data = {}
            for item_key in item_detail:
                if item_key == "Field@0":  # text for the document
                    content = item_detail[item_key]
                elif item_key == "Field@1":  # embedding field for the document
                    continue
                elif item_key == "score":  # L2 distance
                    if scores is not None:
                        score = item_detail[item_key]
                        scores.append(score)
                else:
                    meta_data[item_key] = item_detail[item_key]
            results.append(Document(page_content=content, metadata=meta_data))
        return results

    @classmethod
    def from_texts(
        cls: Type[AwaDB],
        texts: List[str],
        embedding: Optional[Embeddings] = None,
        metadatas: Optional[List[dict]] = None,
        table_name: str = _DEFAULT_TABLE_NAME,
        logging_and_data_dir: Optional[str] = None,
        client: Optional[awadb.Client] = None,
        **kwargs: Any,
    ) -> AwaDB:
        """Create an AwaDB vectorstore from a raw documents.

        Args:
            texts (List[str]): List of texts to add to the table.
            embedding (Optional[Embeddings]): Embedding function. Defaults to None.
            metadatas (Optional[List[dict]]): List of metadatas. Defaults to None.
            table_name (str): Name of the table to create.
            logging_and_data_dir (Optional[str]): Directory of logging and persistence.
            client (Optional[awadb.Client]): AwaDB client

        Returns:
            AwaDB: AwaDB vectorstore.
        """
        awadb_client = cls(
            table_name=table_name,
            embedding_model=embedding,
            log_and_data_dir=logging_and_data_dir,
            client=client,
        )
        awadb_client.add_texts(texts=texts, metadatas=metadatas)
        return awadb_client
