from typing import Sequence, Union

from langplus.agents.agent import AgentOutputParser
from langplus.schema import AgentAction, AgentFinish, OutputParserException


class SelfAskOutputParser(AgentOutputParser):
    followups: Sequence[str] = ("Follow up:", "Followup:")
    finish_string: str = "So the final answer is: "

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        last_line = text.split("\n")[-1]
        if not any([follow in last_line for follow in self.followups]):
            if self.finish_string not in last_line:
                raise OutputParserException(f"Could not parse output: {text}")
            return AgentFinish({"output": last_line[len(self.finish_string) :]}, text)

        after_colon = text.split(":")[-1].strip()
        return AgentAction("Intermediate Answer", after_colon, text)

    @property
    def _type(self) -> str:
        return "self_ask"
