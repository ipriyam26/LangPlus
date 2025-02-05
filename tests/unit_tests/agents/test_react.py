"""Unit tests for ReAct."""

from typing import Any, List, Mapping, Optional, Union

from langplus.agents.react.base import ReActChain, ReActDocstoreAgent
from langplus.agents.tools import Tool
from langplus.callbacks.manager import CallbackManagerForLLMRun
from langplus.docstore.base import Docstore
from langplus.docstore.document import Document
from langplus.llms.base import LLM
from langplus.prompts.prompt import PromptTemplate
from langplus.schema import AgentAction

_PAGE_CONTENT = """This is a page about LangChain.

It is a really cool framework.

What isn't there to love about langchain?

Made in 2022."""

_FAKE_PROMPT = PromptTemplate(input_variables=["input"], template="{input}")


class FakeListLLM(LLM):
    """Fake LLM for testing that outputs elements of a list."""

    responses: List[str]
    i: int = -1

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "fake_list"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        """Increment counter, and then return response in that index."""
        self.i += 1
        return self.responses[self.i]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {}


class FakeDocstore(Docstore):
    """Fake docstore for testing purposes."""

    def search(self, search: str) -> Union[str, Document]:
        """Return the fake document."""
        document = Document(page_content=_PAGE_CONTENT)
        return document


def test_predict_until_observation_normal() -> None:
    """Test predict_until_observation when observation is made normally."""
    outputs = ["foo\nAction: Search[foo]"]
    fake_llm = FakeListLLM(responses=outputs)
    tools = [
        Tool(name="Search", func=lambda x: x, description="foo"),
        Tool(name="Lookup", func=lambda x: x, description="bar"),
    ]
    agent = ReActDocstoreAgent.from_llm_and_tools(fake_llm, tools)
    output = agent.plan([], input="")
    expected_output = AgentAction("Search", "foo", outputs[0])
    assert output == expected_output


def test_react_chain() -> None:
    """Test react chain."""
    responses = [
        "I should probably search\nAction: Search[langchain]",
        "I should probably lookup\nAction: Lookup[made]",
        "Ah okay now I know the answer\nAction: Finish[2022]",
    ]
    fake_llm = FakeListLLM(responses=responses)
    react_chain = ReActChain(llm=fake_llm, docstore=FakeDocstore())
    output = react_chain.run("when was langchain made")
    assert output == "2022"


def test_react_chain_bad_action() -> None:
    """Test react chain when bad action given."""
    bad_action_name = "BadAction"
    responses = [
        f"I'm turning evil\nAction: {bad_action_name}[langchain]",
        "Oh well\nAction: Finish[curses foiled again]",
    ]
    fake_llm = FakeListLLM(responses=responses)
    react_chain = ReActChain(llm=fake_llm, docstore=FakeDocstore())
    output = react_chain.run("when was langchain made")
    assert output == "curses foiled again"
