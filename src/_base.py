"""Base server factory abstraction.

This module provides the abstract base class for all server factory implementations.
It enforces the singleton pattern and provides a common interface for creating,
retrieving, and resetting server instances.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict, TypeVar, Unpack

ServerType = TypeVar("ServerType")


class ServerKwargs(TypedDict, total=False):
    """Base TypedDict for server factory keyword arguments."""

    pass


class BaseServerFactory[ServerType](ABC):
    """Abstract base class for server factories.

    This class provides the foundation for implementing server factories that
    follow the singleton pattern. All concrete server factories must inherit
    from this class and implement the required methods.

    Design Pattern
    ==============
    - Singleton Pattern: Ensures only one instance of each server type exists
    - Factory Pattern: Provides a common interface for creating servers
    - Generic Type Support: Type-safe server instance management

    Implementation Requirements
    ==========================
    Concrete implementations must:
    1. Maintain a private global instance variable
    2. Implement the create() method with singleton enforcement
    3. Implement the get() method that returns the existing instance
    4. Implement the reset() method for testing purposes
    5. Follow proper error handling and assertion patterns

    Examples
    --------
    **Basic Implementation:**

    .. code-block:: python

        from typing import Final
        from ._base import BaseServerFactory

        _MY_SERVER_INSTANCE: MyServer | None = None

        class MyServerFactory(BaseServerFactory[MyServer]):
            @staticmethod
            def create(**kwargs) -> MyServer:
                global _MY_SERVER_INSTANCE
                assert _MY_SERVER_INSTANCE is None, "Server already created"
                _MY_SERVER_INSTANCE = MyServer(**kwargs)
                return _MY_SERVER_INSTANCE

            @staticmethod
            def get() -> MyServer:
                assert _MY_SERVER_INSTANCE is not None, "Server not created"
                return _MY_SERVER_INSTANCE

            @staticmethod
            def reset() -> None:
                global _MY_SERVER_INSTANCE
                _MY_SERVER_INSTANCE = None

    **Usage:**

    .. code-block:: python

        # Create server
        server = MyServerFactory.create(param="value")

        # Get existing server
        server = MyServerFactory.get()

        # Reset for testing
        MyServerFactory.reset()

    """

    @staticmethod
    @abstractmethod
    def create(**kwargs: Unpack[ServerKwargs]) -> ServerType:
        """Create and configure a new server instance.

        This method must implement singleton pattern enforcement to ensure
        only one instance of the server can be created. It should raise
        an AssertionError if an instance already exists.

        Parameters
        ----------
        **kwargs : dict
            Configuration parameters for the server instance

        Returns
        -------
        ServerType
            The newly created server instance

        Raises
        ------
        AssertionError
            If a server instance has already been created

        """
        pass

    @staticmethod
    @abstractmethod
    def get() -> ServerType:
        """Get the existing server instance.

        This method must return the previously created server instance.
        It should raise an AssertionError if no instance has been created yet.

        Returns
        -------
        ServerType
            The existing server instance

        Raises
        ------
        AssertionError
            If no server instance has been created yet

        """
        pass

    @staticmethod
    @abstractmethod
    def reset() -> None:
        """Reset the singleton instance.

        This method must clear the global server instance, allowing a new
        instance to be created. This is primarily used for testing purposes
        to ensure clean state between tests.

        Returns
        -------
        None

        """
        pass
