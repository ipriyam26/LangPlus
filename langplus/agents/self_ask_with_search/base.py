"""Chain that does self ask with search."""
from typing import Any, Sequence, Union

from pydantic import Field

from langplus.agents.agent import Agent, AgentExecutor, AgentOutputParser
from langplus.agents.agent_types import AgentType
from langplus.agents.self_ask_with_search.output_parser import SelfAskOutputParser
from langplus.agents.self_ask_with_search.prompt import PROMPT
from langplus.agents.tools import Tool
from langplus.agents.utils import validate_tools_single_input
from langplus.base_language import BaseLanguageModel
from langplus.prompts.base import BasePromptTemplate
from langplus.tools.base import BaseTool
from langplus.utilities.google_serper import GoogleSerperAPIWrapper
from langplus.utilities.serpapi import SerpAPIWrapper


class SelfAskWithSearchAgent(Agent):
    """Agent for the self-ask-with-search paper."""

    output_parser: AgentOutputParser = Field(default_factory=SelfAskOutputParser)

    @classmethod
    def _get_default_output_parser(cls, **kwargs: Any) -> AgentOutputParser:
        return SelfAskOutputParser()

    @property
    def _agent_type(self) -> str:
        """Return Identifier of agent type."""
        return AgentType.SELF_ASK_WITH_SEARCH

    @classmethod
    def create_prompt(cls, tools: Sequence[BaseTool]) -> BasePromptTemplate:
        """Prompt does not depend on tools."""
        return PROMPT

    @classmethod
    def _validate_tools(cls, tools: Sequence[BaseTool]) -> None:
        validate_tools_single_input(cls.__name__, tools)
        super()._validate_tools(tools)
        if len(tools) != 1:
            raise ValueError(f"Exactly one tool must be specified, but got {tools}")
        tool_names = {tool.name for tool in tools}
        if tool_names != {"Intermediate Answer"}:
            raise ValueError(
                f"Tool name should be Intermediate Answer, got {tool_names}"
            )

    @property
    def observation_prefix(self) -> str:
        """Prefix to append the observation with."""
        return "Intermediate answer: "

    @property
    def llm_prefix(self) -> str:
        """Prefix to append the LLM call with."""
        return ""


class SelfAskWithSearchChain(AgentExecutor):
    """Chain that does self ask with search.

    Example:
        .. code-block:: python

            from langchain import SelfAskWithSearchChain, OpenAI, GoogleSerperAPIWrapper
            search_chain = GoogleSerperAPIWrapper()
            self_ask = SelfAskWithSearchChain(llm=OpenAI(), search_chain=search_chain)
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        search_chain: Union[GoogleSerperAPIWrapper, SerpAPIWrapper],
        **kwargs: Any,
    ):
        """Initialize with just an LLM and a search chain."""
        search_tool = Tool(
            name="Intermediate Answer",
            func=search_chain.run,
            coroutine=search_chain.arun,
            description="Search",
        )
        agent = SelfAskWithSearchAgent.from_llm_and_tools(llm, [search_tool])
        super().__init__(agent=agent, tools=[search_tool], **kwargs)
