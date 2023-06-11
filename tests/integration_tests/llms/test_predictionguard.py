"""Test Prediction Guard API wrapper."""

from langplus.llms.predictionguard import PredictionGuard


def test_predictionguard_call() -> None:
    """Test valid call to prediction guard."""
    llm = PredictionGuard(model="OpenAI-text-davinci-003")
    output = llm("Say foo:")
    assert isinstance(output, str)
