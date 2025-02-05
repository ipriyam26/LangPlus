"""Tool for the Serper.dev Google Search API."""

from typing import Optional

from pydantic.fields import Field

from langplus.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langplus.tools.base import BaseTool
from langplus.utilities.google_serper import GoogleSerperAPIWrapper


class GoogleSerperRun(BaseTool):
    """Tool that adds the capability to query the Serper.dev Google search API."""

    name = "Google Serper"
    description = (
        "A low-cost Google Search API."
        "Useful for when you need to answer questions about current events."
        "Input should be a search query."
    )
    api_wrapper: GoogleSerperAPIWrapper

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.run(query))

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return (await self.api_wrapper.arun(query)).__str__()


class GoogleSerperResults(BaseTool):
    """Tool that has capability to query the Serper.dev Google Search API
    and get back json."""

    name = "Google Serrper Results JSON"
    description = (
        "A low-cost Google Search API."
        "Useful for when you need to answer questions about current events."
        "Input should be a search query. Output is a JSON object of the query results"
    )
    api_wrapper: GoogleSerperAPIWrapper = Field(default_factory=GoogleSerperAPIWrapper)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.results(query))

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        return (await self.api_wrapper.aresults(query)).__str__()
