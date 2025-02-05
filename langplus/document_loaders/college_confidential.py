"""Loader that loads College Confidential."""
from typing import List

from langplus.docstore.document import Document
from langplus.document_loaders.web_base import WebBaseLoader


class CollegeConfidentialLoader(WebBaseLoader):
    """Loader that loads College Confidential webpages."""

    def load(self) -> List[Document]:
        """Load webpage."""
        soup = self.scrape()
        text = soup.select_one("main[class='skin-handler']").text
        metadata = {"source": self.web_path}
        return [Document(page_content=text, metadata=metadata)]
