"""Test splitting with page numbers included."""
import os

from langplus.document_loaders import PyPDFLoader
from langplus.embeddings.openai import OpenAIEmbeddings
from langplus.vectorstores import FAISS


def test_pdf_pagesplitter() -> None:
    """Test splitting with page numbers included."""
    script_dir = os.path.dirname(__file__)
    loader = PyPDFLoader(os.path.join(script_dir, "examples/hello.pdf"))
    docs = loader.load()
    assert "page" in docs[0].metadata
    assert "source" in docs[0].metadata

    faiss_index = FAISS.from_documents(docs, OpenAIEmbeddings())
    docs = faiss_index.similarity_search("Complete this sentence: Hello", k=1)
    assert "Hello world" in docs[0].page_content
