"""Wrapper around HazyResearch's Manifest library."""
from typing import Any, Dict, List, Mapping, Optional

from pydantic import Extra, root_validator

from langplus.callbacks.manager import CallbackManagerForLLMRun
from langplus.llms.base import LLM


class ManifestWrapper(LLM):
    """Wrapper around HazyResearch's Manifest library."""

    client: Any  #: :meta private:
    llm_kwargs: Optional[Dict] = None

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that python package exists in environment."""
        try:
            from manifest import Manifest

            if not isinstance(values["client"], Manifest):
                raise ValueError
        except ImportError:
            raise ValueError(
                "Could not import manifest python package. "
                "Please install it with `pip install manifest-ml`."
            )
        return values

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        kwargs = self.llm_kwargs or {}
        return {**self.client.client.get_model_params(), **kwargs}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "manifest"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        """Call out to LLM through Manifest."""
        if stop is not None and len(stop) != 1:
            raise NotImplementedError(
                f"Manifest currently only supports a single stop token, got {stop}"
            )
        kwargs = self.llm_kwargs or {}
        if stop is not None:
            kwargs["stop_token"] = stop
        return self.client.run(prompt, **kwargs)
