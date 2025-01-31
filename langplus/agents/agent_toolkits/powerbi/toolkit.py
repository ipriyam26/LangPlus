"""Toolkit for interacting with a Power BI dataset."""
from typing import List, Optional

from pydantic import Field

from langplus.agents.agent_toolkits.base import BaseToolkit
from langplus.base_language import BaseLanguageModel
from langplus.callbacks.base import BaseCallbackManager
from langplus.chains.llm import LLMChain
from langplus.prompts import PromptTemplate
from langplus.tools import BaseTool
from langplus.tools.powerbi.prompt import QUESTION_TO_QUERY
from langplus.tools.powerbi.tool import (
    InfoPowerBITool,
    ListPowerBITool,
    QueryPowerBITool,
)
from langplus.utilities.powerbi import PowerBIDataset


class PowerBIToolkit(BaseToolkit):
    """Toolkit for interacting with PowerBI dataset."""

    powerbi: PowerBIDataset = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)
    examples: Optional[str] = None
    max_iterations: int = 5
    callback_manager: Optional[BaseCallbackManager] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        if self.callback_manager:
            chain = LLMChain(
                llm=self.llm,
                callback_manager=self.callback_manager,
                prompt=PromptTemplate(
                    template=QUESTION_TO_QUERY,
                    input_variables=["tool_input", "tables", "schemas", "examples"],
                ),
            )
        else:
            chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    template=QUESTION_TO_QUERY,
                    input_variables=["tool_input", "tables", "schemas", "examples"],
                ),
            )
        return [
            QueryPowerBITool(
                llm_chain=chain,
                powerbi=self.powerbi,
                examples=self.examples,
                max_iterations=self.max_iterations,
            ),
            InfoPowerBITool(powerbi=self.powerbi),
            ListPowerBITool(powerbi=self.powerbi),
        ]
