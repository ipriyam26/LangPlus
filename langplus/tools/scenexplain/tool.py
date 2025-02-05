"""Tool for the SceneXplain API."""
from typing import Optional

from pydantic import BaseModel, Field

from langplus.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langplus.tools.base import BaseTool
from langplus.utilities.scenexplain import SceneXplainAPIWrapper


class SceneXplainInput(BaseModel):
    """Input for SceneXplain."""

    query: str = Field(..., description="The link to the image to explain")


class SceneXplainTool(BaseTool):
    """Tool that adds the capability to explain images."""

    name = "Image Explainer"
    description = (
        "An Image Captioning Tool: Use this tool to generate a detailed caption "
        "for an image. The input can be an image file of any format, and "
        "the output will be a text description that covers every detail of the image."
    )
    api_wrapper: SceneXplainAPIWrapper = Field(default_factory=SceneXplainAPIWrapper)

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(query)

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SceneXplainTool does not support async")
