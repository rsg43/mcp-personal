"""
Module for interacting with the Anthropic API.
"""

from os import environ

from langchain_anthropic.chat_models import ChatAnthropic

from mcp_personal.clients.model.base import BaseModel


class AnthropicModel(BaseModel):
    """
    Model class for interacting with the Anthropic API.
    """

    def __init__(self) -> None:
        self._model = ChatAnthropic(  # type: ignore[call-arg]
            model_name="claude-3-haiku-20240307",
            temperature=0.3,
            max_tokens_to_sample=1024,
            timeout=60,
            max_retries=3,
            api_key=environ.get("ANTHROPIC_API_KEY"),  # type: ignore[arg-type]
        )
