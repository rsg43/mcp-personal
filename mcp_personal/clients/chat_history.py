"""
Module for managing conversation history in a SQL database.
"""

from langchain_core.messages import BaseMessage
from langchain_community.chat_message_histories.sql import (
    SQLChatMessageHistory,
)

from sqlalchemy import create_engine


class ChatHistory:
    """
    Class for managing chat history using a SQL database. This class provides
    methods to get, add, and clear messages for a specific session.
    """

    def __init__(self) -> None:
        self._engine = create_engine(url="sqlite:///chat_history.db")

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        """
        Retrieve messages for a given session ID.

        :param session_id: The ID of the session for which to retrieve
            messages.
        :type session_id: str
        :return: A list of messages associated with the session.
        :rtype: list[BaseMessage]
        """
        return SQLChatMessageHistory(
            connection=self._engine,
            session_id=session_id,
        ).get_messages()

    def add_messages(
        self, session_id: str, messages: list[BaseMessage]
    ) -> None:
        """
        Add messages to the chat history for a specific session.

        :param session_id: The ID of the session to which messages will be
            added.
        :type session_id: str
        :param messages: A list of messages to add to the chat history.
        :type messages: list[BaseMessage]
        """
        SQLChatMessageHistory(
            connection=self._engine,
            session_id=session_id,
        ).add_messages(messages=messages)

    def clear(self, session_id: str) -> None:
        """
        Clear all messages for a specific session ID.

        :param session_id: The ID of the session for which to clear messages.
        :type session_id: str
        """
        SQLChatMessageHistory(
            connection=self._engine,
            session_id=session_id,
        ).clear()
