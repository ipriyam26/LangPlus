"""Test Replicate API wrapper."""

from langplus.llms.replicate import Replicate


def test_replicate_call() -> None:
    """Test valid call to Replicate."""
    llm = Replicate()
    output = llm("Say foo:")
    assert isinstance(output, str)
