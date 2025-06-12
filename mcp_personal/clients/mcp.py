"""
Module for MCP client that interacts with MCP servers.
"""

from typing import Any
from types import TracebackType
from contextlib import AsyncExitStack

from typing_extensions import Self
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.types import TextContent
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    BaseMessage,
    ToolMessage,
)

from mcp_personal.clients.chat_history import ChatHistory
from mcp_personal.clients.model.anthropic import AnthropicModel

SYSTEM_PROMPT_TEMPLATE = (
    "You are a helpful assistant. Try to answer questions concisely and "
    "accuretely. You are also able to call tools to help you answer questions"
    ". Only use tools if the question requires it. "
    "Here are the tools you can use: \n\n{tools}\n\n"
)

SERVERS: dict[str, str | StdioServerParameters] = {
    "maths": "http://localhost:54321/sse",
    "notion": StdioServerParameters(
        command="docker",
        args=["run", "--rm", "-i", "-e", "OPENAPI_MCP_HEADERS", "mcp/notion"],
        env={
            "OPENAPI_MCP_HEADERS": '{"Authorization":"Bearer ntn_****","Notion-Version":"2022-06-28"}'
        },
    ),
}


class MCPClient:
    """
    MCPClient is an asynchronous client for interacting with the MCP servers.
    It manages sessions, handles tool calls, and processes queries through a
    model. It also maintains a chat history for each session.
    """

    def __init__(self) -> None:
        self.chat_history = ChatHistory()
        self.sessions: list[ClientSession] = []
        self.exit_stack = AsyncExitStack()
        self.tool_sessions: dict[str, ClientSession] = {}
        self._model = AnthropicModel()
        self._system_prompt = SYSTEM_PROMPT_TEMPLATE
        self._all_tools: list[dict[str, Any]] = []

    async def __aenter__(self) -> Self:
        """
        Asynchronous context manager entry method to initialize the MCP client.

        :return: The initialized MCPClient instance.
        :rtype: Self
        """
        await self.connect_to_servers()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Asynchronous context manager exit method to clean up the MCP client.

        :param exc_type: The type of exception raised, if any.
        :type exc_type: type[BaseException] | None
        :param exc_value: The exception instance, if any.
        :type exc_value: BaseException | None
        :param traceback: The traceback of the exception, if any.
        :type traceback: TracebackType | None
        """
        await self.close()

    async def connect_to_servers(self) -> None:
        """
        Connect to the MCP servers and initialize sessions for each tool.
        This method retrieves the list of tools from each server and binds them
        to the model for use in the client.
        """
        for _, server_params in SERVERS.items():
            if isinstance(server_params, str):
                sse_transport = await self.exit_stack.enter_async_context(
                    sse_client(server_params)
                )
                session = await self.exit_stack.enter_async_context(
                    ClientSession(*sse_transport)
                )
            else:
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                session = await self.exit_stack.enter_async_context(
                    ClientSession(*stdio_transport)
                )

            await session.initialize()
            self.sessions.append(session)

            response = await session.list_tools()
            tools = response.tools

            for tool in tools:
                self.tool_sessions[tool.name] = session
                self._all_tools.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                )

        self._model.bind_tools(self._all_tools)

    async def invoke(self, query: str, session_id: str) -> list[BaseMessage]:
        """
        Invoke the MCP client with a query and session ID, processing the query
        through the model and tools, and returning the response messages.

        :param query: The query to process.
        :type query: str
        :param session_id: The session ID for tracking the conversation.
        :type session_id: str
        :return: A list of messages containing the response from the model and
            any tool calls.
        :rtype: list[BaseMessage]
        """
        messages = [
            SystemMessage(
                content=self._system_prompt.format(tools=self._all_tools)
            )
        ] + self.chat_history.get_messages(session_id)
        query_message = HumanMessage(content=query)
        new_messages: list[BaseMessage] = []
        response = self._model.chat(messages + [query_message] + new_messages)
        new_messages.append(response)

        while len(response.tool_calls) > 0:
            for tool_call in response.tool_calls:
                result = await self.tool_sessions[tool_call["name"]].call_tool(
                    name=tool_call["name"], arguments=tool_call["args"]
                )

                new_messages.append(
                    ToolMessage(
                        content=result.content,  # type: ignore[arg-type]
                        artifact={
                            "call": tool_call,
                            "result": (
                                result.content[0].text
                                if isinstance(result.content[0], TextContent)
                                else result.content[0]
                            ),
                        },
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
            response = self._model.chat(
                messages + [query_message] + new_messages
            )
            new_messages.append(response)

        self.chat_history.add_messages(
            messages=new_messages, session_id=session_id
        )

        return new_messages

    async def close(self) -> None:
        """
        Close the MCP client and all sessions.
        """
        await self.exit_stack.aclose()
