"""Tool for the Arxiv API."""

from typing import Optional

from langplus.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langplus.tools.base import BaseTool
from langplus.utilities.arxiv import ArxivAPIWrapper


class ArxivQueryRun(BaseTool):
    """Tool that adds the capability to search using the Arxiv API."""

    name = "Arxiv"
    description = (
        "A wrapper around Arxiv.org "
        "Useful for when you need to answer questions about Physics, Mathematics, "
        "Computer Science, Quantitative Biology, Quantitative Finance, Statistics, "
        "Electrical Engineering, and Economics "
        "from scientific articles on arxiv.org. "
        "Input should be a search query."
    )
    api_wrapper: ArxivAPIWrapper

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Arxiv tool."""
        return self.api_wrapper.run(query)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Arxiv tool asynchronously."""
        raise NotImplementedError("ArxivAPIWrapper does not support async")
