from typing import Any, Dict, List, Tuple

from pydantic import root_validator

from langplus.prompts.base import BasePromptTemplate
from langplus.prompts.chat import BaseChatPromptTemplate
from langplus.schema import PromptValue


def _get_inputs(inputs: dict, input_variables: List[str]) -> dict:
    return {k: inputs[k] for k in input_variables}


class PipelinePromptTemplate(BasePromptTemplate):
    """A prompt template for composing multiple prompts together.

    This can be useful when you want to reuse parts of prompts.
    A PipelinePrompt consists of two main parts:
        - final_prompt: This is the final prompt that is returned
        - pipeline_prompts: This is a list of tuples, consisting
            of a string (`name`) and a Prompt Template.
            Each PromptTemplate will be formatted and then passed
            to future prompt templates as a variable with
            the same name as `name`
    """

    final_prompt: BasePromptTemplate
    pipeline_prompts: List[Tuple[str, BasePromptTemplate]]

    @root_validator(pre=True)
    def get_input_variables(cls, values: Dict) -> Dict:
        """Get input variables."""
        created_variables = set()
        all_variables = set()
        for k, prompt in values["pipeline_prompts"]:
            created_variables.add(k)
            all_variables.update(prompt.input_variables)
        values["input_variables"] = list(all_variables.difference(created_variables))
        return values

    def format_prompt(self, **kwargs: Any) -> PromptValue:
        for k, prompt in self.pipeline_prompts:
            _inputs = _get_inputs(kwargs, prompt.input_variables)
            if isinstance(prompt, BaseChatPromptTemplate):
                kwargs[k] = prompt.format_messages(**_inputs)
            else:
                kwargs[k] = prompt.format(**_inputs)
        _inputs = _get_inputs(kwargs, self.final_prompt.input_variables)
        return self.final_prompt.format_prompt(**_inputs)

    def format(self, **kwargs: Any) -> str:
        return self.format_prompt(**kwargs).to_string()

    @property
    def _prompt_type(self) -> str:
        raise ValueError
