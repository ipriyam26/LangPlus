"""Loader that loads .txt web files."""
from typing import List

from langplus.docstore.document import Document
from langplus.document_loaders.base import BaseLoader


class GutenbergLoader(BaseLoader):
    """Loader that uses urllib to load .txt web files."""

    def __init__(self, file_path: str):
        """Initialize with file path."""
        if not file_path.startswith("https://www.gutenberg.org"):
            raise ValueError("file path must start with 'https://www.gutenberg.org'")

        if not file_path.endswith(".txt"):
            raise ValueError("file path must end with '.txt'")

        self.file_path = file_path

    def load(self) -> List[Document]:
        """Load file."""
        from urllib.request import urlopen

        elements = urlopen(self.file_path)
        text = "\n\n".join([str(el.decode("utf-8-sig")) for el in elements])
        metadata = {"source": self.file_path}
        return [Document(page_content=text, metadata=metadata)]
