from typing import Dict, List, Optional, cast

from langplus.docstore.document import Document
from langplus.document_loaders.base import BaseLoader


class DuckDBLoader(BaseLoader):
    """Loads a query result from DuckDB into a list of documents.

    Each document represents one row of the result. The `page_content_columns`
    are written into the `page_content` of the document. The `metadata_columns`
    are written into the `metadata` of the document. By default, all columns
    are written into the `page_content` and none into the `metadata`.
    """

    def __init__(
        self,
        query: str,
        database: str = ":memory:",
        read_only: bool = False,
        config: Optional[Dict[str, str]] = None,
        page_content_columns: Optional[List[str]] = None,
        metadata_columns: Optional[List[str]] = None,
    ):
        self.query = query
        self.database = database
        self.read_only = read_only
        self.config = config or {}
        self.page_content_columns = page_content_columns
        self.metadata_columns = metadata_columns

    def load(self) -> List[Document]:
        try:
            import duckdb
        except ImportError:
            raise ImportError(
                "Could not import duckdb python package. "
                "Please install it with `pip install duckdb`."
            )

        docs = []
        with duckdb.connect(
            database=self.database, read_only=self.read_only, config=self.config
        ) as con:
            query_result = con.execute(self.query)
            results = query_result.fetchall()
            description = cast(list, query_result.description)
            field_names = [c[0] for c in description]

            if self.page_content_columns is None:
                page_content_columns = field_names
            else:
                page_content_columns = self.page_content_columns

            if self.metadata_columns is None:
                metadata_columns = []
            else:
                metadata_columns = self.metadata_columns

            for result in results:
                page_content = "\n".join(
                    f"{column}: {result[field_names.index(column)]}"
                    for column in page_content_columns
                )

                metadata = {
                    column: result[field_names.index(column)]
                    for column in metadata_columns
                }

                doc = Document(page_content=page_content, metadata=metadata)
                docs.append(doc)

        return docs
