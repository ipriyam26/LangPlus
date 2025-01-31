"""Test StochasticAI API wrapper."""

from langplus.llms.stochasticai import StochasticAI


def test_stochasticai_call() -> None:
    """Test valid call to StochasticAI."""
    llm = StochasticAI()
    output = llm("Say foo:")
    assert isinstance(output, str)
