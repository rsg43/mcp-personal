"""
Module for the BaseModel class, which provides a unified interface
for interacting with various language models.
"""

from typing import Any, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import Runnable
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel


class BaseModel:
    """
    Base class for interacting with a language model. Provides methods to
    chat with the model and invoke it with a prompt. Can also bind tools to
    the model for enhanced functionality."""

    _model: BaseChatModel
    _tools_bound: bool = False
    _tool_model: Optional[Runnable[LanguageModelInput, BaseMessage]]

    def chat(self, messages: list[BaseMessage]) -> AIMessage:
        """
        Method to send a list of messages to the model and generated the next
        response based on the messages.

        :param messages: List of messages to send to the model.
        :type messages: list[BaseMessage]
        :raises TypeError: If the model's response is not an instance of
            AIMessage.
        :return: The model's response message.
        :rtype: AIMessage
        """
        if self._tools_bound and self._tool_model:
            result = self._tool_model.invoke(input=messages)
        else:
            result = self._model.invoke(input=messages)

        if not isinstance(result, AIMessage):
            raise TypeError(f"Expected AIMessage, got {type(result).__name__}")
        return result

    def invoke(self, prompt: str) -> str:
        """
        Method to send a prompt to the model and get the response.

        :param prompt: The prompt to send to the model.
        :type prompt: str
        :raises TypeError: If the model's response is not a string.
        :return: The model's response.
        :rtype: str
        """
        if self._tools_bound and self._tool_model:
            result = self._tool_model.invoke(
                input=[HumanMessage(content=prompt)]
            ).content
        else:
            result = self._model.invoke(
                input=[HumanMessage(content=prompt)]
            ).content

        if not isinstance(result, str):
            raise TypeError(f"Expected str, got {type(result).__name__}")

        return result

    def bind_tools(self, tools: list[dict[str, Any]]) -> None:
        """
        Method to bind tools to the model.

        :param tools: List of tool names to bind to the model.
        :type tools: list[dict[str, Any]]
        """
        self._tool_model = self._model.bind_tools(tools)
        self._tools_bound = True
