"""
Module for the Async Web API service. This can be used to create a web API,
which uses an underlying web app to register endpoints and serve the app on the
specified host and port. It can be used to present functionality behind
specified endpoints, which can be called by clients to interact with the
service.
"""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Union, Callable, Any
from typing_extensions import Self

from mcp_personal.web_api.app import WebApp, WebAppConfig


class BaseWebAPI(ABC):
    """
    Base Web API service, which contains the run method to start the web API
    and requires implementations to add endpoint handlers to the web app.
    """

    def __init__(self, host: str, port: int) -> None:
        self._app = WebApp(
            config=WebAppConfig(
                host=host,
                port=port,
                threads=4,
                connection_limit=100,
            )
        )

    @property
    @abstractmethod
    def _endpoint_handlers(
        self,
    ) -> dict[str, tuple[list[str], str, Callable[..., Any]]]:
        """
        Property to get the endpoint handlers. This should be implemented by
        subclasses to provide the actual endpoint handlers.

        :return: The endpoint handlers.
        :rtype: dict[str, tuple[list[str], str, Callable[..., Any]]]
        """

    def __enter__(self) -> Self:
        """
        Method to enter the context manager.

        :return: The web API service.
        :rtype: Self
        """
        return self

    def __exit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: Union[TracebackType, None],
    ) -> None:
        """
        Method to exit the context manager.

        :param exc_type: The exception type.
        :type exc_type: Union[type[BaseException], None]
        :param exc_val: The exception value.
        :type exc_val: Union[BaseException, None]
        :param exc_tb: The exception traceback.
        :type exc_tb: Union[TracebackType, None]
        """

    def run(self) -> None:
        """
        Run the web API. This method adds the endpoint handlers to the web app
        and starts the server.
        """
        for name, (
            methods,
            endpoint,
            handler,
        ) in self._endpoint_handlers.items():
            self._app.add_endpoint(
                endpoint,
                name,
                handler,
                methods,
            )

        self._app.run()
