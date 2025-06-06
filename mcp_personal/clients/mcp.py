from typing import Any
from types import TracebackType
from contextlib import AsyncExitStack
from asyncio import run
from uuid import uuid4

from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    BaseMessage,
    ToolMessage,
)
from mcp.types import TextContent

from mcp_personal.clients.chat_history import ChatHistory
from mcp_personal.clients.model.anthropic import AnthropicModel

SYSTEM_PROMPT_TEMPLATE = (
    "You are a helpful assistant. Try to answer questions concisely and "
    "accuretely. You are also able to call tools to help you answer questions"
    ". Only use tools if the question requires it. "
    "Here are the tools you can use: \n\n{tools}\n\n"
)

SERVERS = {
    "maths": "http://localhost:54321/sse",
}


class MCPClient:

    def __init__(self) -> None:
        self.chat_history = ChatHistory()
        self.sessions: list[ClientSession] = []
        self.exit_stack = AsyncExitStack()
        self.tool_sessions: dict[str, ClientSession] = {}
        self._model = AnthropicModel()
        self._system_prompt = SYSTEM_PROMPT_TEMPLATE
        self._all_tools: list[dict[str, Any]] = []

    async def __aenter__(self):
        await self.connect_to_servers()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def connect_to_servers(self) -> None:
        for _, server_params in SERVERS.items():
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(server_params)
            )
            session = await self.exit_stack.enter_async_context(
                ClientSession(*sse_transport)
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
            print(f"AI: {response.content[0]["text"]}")
            for tool_call in response.tool_calls:
                print(
                    f'Tool: {tool_call["name"]}, arguments {tool_call["args"]}'
                )
                result = await self.tool_sessions[tool_call["name"]].call_tool(
                    name=tool_call["name"], arguments=tool_call["args"]
                )
                print(f"Tool call completed: {tool_call['name']}")

                print_result = (
                    val.text
                    if isinstance(val := result.content[0], TextContent)
                    else val
                )
                print(f"Result: {print_result}")

                new_messages.append(
                    ToolMessage(
                        content=result.content,
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

        print(f"AI: {response.content}")

        self.chat_history.add_messages(
            messages=new_messages, session_id=session_id
        )

        return new_messages

    async def run(self) -> None:
        print("\nMCP Client Running! (enter q to quit)")
        session_id = uuid4().hex
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "q":
                    break

                await self.invoke(
                    query=query,
                    session_id=session_id,
                )
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def close(self) -> None:
        await self.exit_stack.aclose()


async def main() -> None:
    async with MCPClient() as client:
        await client.run()


def start_client() -> None:
    run(main())
