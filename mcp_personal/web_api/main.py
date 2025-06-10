"""
Module for the Async Web API service. This can be used to create a web API,
which uses an underlying web app to register endpoints and serve the app on the
specified host and port. It can be used to present functionality behind
specified endpoints, which can be called by clients to interact with the
service.
"""

import asyncio
from typing import Callable, Any
from types import TracebackType
import json

from typing_extensions import Self
from quart import Response

from mcp_personal.web_api.api import BaseWebAPI
from mcp_personal.clients.mcp import MCPClient


class AsyncWebAPI(BaseWebAPI):
    """
    Base Web API service, which contains the run method to start the web API
    and requires implementations to add endpoint handlers to the web app.
    """

    def __init__(self) -> None:
        super().__init__(
            host="0.0.0.0",
            port=12345,
        )
        self._mcp_client = MCPClient()

    async def __aenter__(self) -> Self:
        """
        Asynchronous context manager entry method. This is used to start the
        web API service when entering the context.

        :return: The instance of the AsyncWebAPI.
        :rtype: Self
        """
        super().__enter__()
        await self._mcp_client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Asynchronous context manager exit method. This is used to stop the
        web API service when exiting the context.

        :param exc_type: The type of the exception raised, if any.
        :type exc_type: type[BaseException] | None
        :param exc_value: The value of the exception raised, if any.
        :type exc_value: BaseException | None
        :param traceback: The traceback of the exception raised, if any.
        :type traceback: TracebackType | None
        """
        await self._mcp_client.__aexit__(exc_type, exc_value, traceback)
        super().__exit__(exc_type, exc_value, traceback)

    @property
    def _endpoint_handlers(
        self,
    ) -> dict[str, tuple[list[str], str, Callable[..., Any]]]:
        """
        Property to get the endpoint handlers. This should be implemented by
        subclasses to provide the actual endpoint handlers.

        :return: The endpoint handlers.
        :rtype: dict[str, tuple[list[str], str, Callable[..., Any]]]
        """
        return {
            "homepage": (["GET"], "/", self._create_homepage),
            "invoke": (["POST"], "/invoke", self._invoke),
        }

    async def _create_homepage(self, params: dict[str, Any]) -> Response:
        """
        Handler for creating the Async Quart API homepage. This is a GET
        request, which does not require any data to be passed in the request
        and simply returns a welcome message.

        :param params: The request parameters.
        :type params: dict[str, Any]
        :return: The response.
        :rtype: Response
        """
        _ = params
        return Response(
            "<h1> Hello, welcome to the Async Quart API homepage! </h1>", 200
        )

    async def _invoke(self, data: str, params: dict[str, Any]) -> Response:
        """
        Handler for invoking the MCP client with a query. This is a POST
        request, which requires a query to be passed in the request data and
        returns the response from the MCP client.

        :param data: The request data.
        :type data: str
        :param params: The request parameters.
        :type params: dict[str, Any]
        :return: The response.
        :rtype: Response
        """
        _ = params
        try:
            data_dict = json.loads(data)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", 400)

        try:
            query = data_dict["query"]
        except KeyError:
            return Response("Query is required", 400)

        try:
            session_id = data_dict["session_id"]
        except KeyError:
            return Response("Session ID is required", 400)

        messages = await self._mcp_client.invoke(
            query=query, session_id=session_id
        )
        response = {
            "messages": [message.to_json() for message in messages],
            "session_id": session_id,
        }
        return Response(json.dumps(response), 200)


async def _start_async_api() -> None:
    """
    Function to start the Async Web API service. This is used to create an
    instance of the AsyncWebAPI and run it.
    """
    async with AsyncWebAPI() as app:
        await app.run()


def start_async_api() -> None:
    """
    Function to start the Async Web API service. This is used to create an
    instance of the AsyncWebAPI and run it.
    """
    asyncio.run(_start_async_api())
