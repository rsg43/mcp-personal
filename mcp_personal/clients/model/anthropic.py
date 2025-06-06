from langchain_anthropic.chat_models import ChatAnthropic

from mcp_personal.clients.model.base import BaseModel


class AnthropicModel(BaseModel):

    def __init__(self, api_key: str = None) -> None:
        self._model = ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.3,
            max_tokens=1024,
            timeout=60,
            max_retries=3,
            api_key=api_key,
        )
