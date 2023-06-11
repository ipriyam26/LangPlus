"""Test RetrievalQA functionality."""
from pathlib import Path

from langplus.chains import RetrievalQA
from langplus.chains.loading import load_chain
from langplus.document_loaders import TextLoader
from langplus.embeddings.openai import OpenAIEmbeddings
from langplus.llms import OpenAI
from langplus.text_splitter import CharacterTextSplitter
from langplus.vectorstores import Chroma


def test_retrieval_qa_saving_loading(tmp_path: Path) -> None:
    """Test saving and loading."""
    loader = TextLoader("docs/modules/state_of_the_union.txt")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_documents(texts, embeddings)
    qa = RetrievalQA.from_llm(llm=OpenAI(), retriever=docsearch.as_retriever())

    file_path = tmp_path / "RetrievalQA_chain.yaml"
    qa.save(file_path=file_path)
    qa_loaded = load_chain(file_path, retriever=docsearch.as_retriever())

    assert qa_loaded == qa
