"""
Module for the Quart web app. This module contains the class for the production
web app, which uses Quart to create a web application that is used by the Web
API to enable communication.
"""

from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from quart import Quart, request
from quart_cors import cors
from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig


@dataclass
class WebAppConfig:
    """
    The web application configuration for the common module. This is used
    to set the host, port, threads and connection limit.

    :param host: Host of the web app.
    :type host: str
    :param port: Port of the web app.
    :type port: int
    :param threads: Number of threads for the web app.
    :type threads: int
    :param connection_limit: Connection limit for the web app.
    :type connection_limit: int
    """

    host: str
    port: int
    threads: int
    connection_limit: int


class WebApp:
    """
    Class for production web app. This class uses Quart to create a web
    application, along with registering endpoints and serving the app on the
    specified host and port.

    :param config: The configuration for the web app.
    :type config: WebAppConfig
    """

    def __init__(self, config: WebAppConfig) -> None:
        self._app = cors(Quart(__name__))
        self._config = config

    async def run(self) -> None:
        """
        Method to run the web app. This will start the web app and listen for
        incoming requests.
        """
        config = HypercornConfig()
        config.bind = [f"{self._config.host}:{self._config.port}"]
        await serve(
            app=self._app,
            config=config,
        )

    def add_endpoint(
        self,
        endpoint: str,
        endpoint_name: str,
        handler: Callable[..., Awaitable[Any]],
        methods: list[str],
    ) -> None:
        """
        Method to add an endpoint to the web app. This must be done before
        starting the application and will set out the handler, methods,
        endpoint address and format (e.g. any variable parts of the endpoint).

        :param endpoint: Path of the endpoint.
        :type endpoint: str
        :param endpoint_name: Name of the endpoint.
        :type endpoint_name: str
        :param handler: Handler callable for the endpoint.
        :type handler: Callable[..., Awaitable[Any]]
        :param methods: List of HTTP methods for the endpoint.
        :type methods: list[str]
        """
        self._app.add_url_rule(
            endpoint,
            endpoint_name,
            self._wrap_handler(handler, methods),
            methods=methods,
        )

    def _wrap_handler(
        self,
        handler: Callable[..., Awaitable[Any]],
        methods: list[str],
    ) -> Callable[..., Awaitable[Any]]:
        """
        Wraps the handler function to accept the request data and arguments as
        parameters. This allows us to use special properties of requests, such
        as the query parameters and request body, and have different behaviour
        for different endpoint methods.

        :param handler: The handler function to wrap.
        :type handler: Callable[..., Awaitable[Any]]
        :param methods: The HTTP methods that the handler accepts.
        :type methods: list[str]
        :raises ValueError: If the method is not supported.
        :return: The wrapped handler function.
        :rtype: Callable[..., Awaitable[Any]]
        """
        (method,) = methods
        if method == "GET":

            async def _handler(*args: Any, **kwargs: Any) -> Any:
                return await handler(request.args.to_dict(), *args, **kwargs)

        elif method in ["POST", "PATCH", "PUT"]:

            async def _handler(*args: Any, **kwargs: Any) -> Any:
                data = await request.data
                return await handler(
                    data.decode(),
                    request.args.to_dict(),
                    *args,
                    **kwargs,
                )

        else:
            raise ValueError(f"Unsupported method: {method}")

        return _handler
