"""Fake LLM wrapper for testing purposes."""
from typing import Any, List, Mapping, Optional, cast

from pydantic import validator

from langplus.callbacks.manager import CallbackManagerForLLMRun
from langplus.llms.base import LLM


class FakeLLM(LLM):
    """Fake LLM wrapper for testing purposes."""

    queries: Optional[Mapping] = None
    sequential_responses: Optional[bool] = False
    response_index: int = 0

    @validator("queries", always=True)
    def check_queries_required(
        cls, queries: Optional[Mapping], values: Mapping[str, Any]
    ) -> Optional[Mapping]:
        if values.get("sequential_response") and not queries:
            raise ValueError(
                "queries is required when sequential_response is set to True"
            )
        return queries

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "fake"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        if self.sequential_responses:
            return self._get_next_response_in_sequence

        if self.queries is not None:
            return self.queries[prompt]
        if stop is None:
            return "foo"
        else:
            return "bar"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {}

    @property
    def _get_next_response_in_sequence(self) -> str:
        queries = cast(Mapping, self.queries)
        response = queries[list(queries.keys())[self.response_index]]
        self.response_index = self.response_index + 1
        return response
