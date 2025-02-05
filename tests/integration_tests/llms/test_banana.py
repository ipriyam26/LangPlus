"""Test BananaDev API wrapper."""

from langplus.llms.bananadev import Banana


def test_banana_call() -> None:
    """Test valid call to BananaDev."""
    llm = Banana()
    output = llm("Say foo:")
    assert isinstance(output, str)
