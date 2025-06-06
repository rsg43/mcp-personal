from langchain_core.messages import BaseMessage
from langchain_community.chat_message_histories.sql import (
    SQLChatMessageHistory,
)

from sqlalchemy import create_engine


class ChatHistory:

    def __init__(self) -> None:
        self._engine = create_engine(url="sqlite:///chat_history.db")

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        return SQLChatMessageHistory(
            connection=self._engine,
            session_id=session_id,
        ).get_messages()

    def add_messages(
        self, session_id: str, messages: list[BaseMessage]
    ) -> None:
        SQLChatMessageHistory(
            connection=self._engine,
            session_id=session_id,
        ).add_messages(messages=messages)

    def clear(self, session_id: str) -> None:
        SQLChatMessageHistory(
            connection=self._engine,
            session_id=session_id,
        ).clear()
