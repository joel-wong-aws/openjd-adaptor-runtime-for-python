# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

from __future__ import annotations

import os
from threading import Event
from pywintypes import HANDLE

from ._named_pipe_request_handler import WinAdaptorServerResourceRequestHandler
from .._named_pipe import ResourceRequestHandler
from .._named_pipe.named_pipe_server import NamedPipeServer


from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:  # pragma: no cover because pytest will think we should test for this.
    from ..adaptors import BaseAdaptor
    from ._actions_queue import ActionsQueue


class WinAdaptorServer(NamedPipeServer):
    """
    This is the Adaptor server which will be passed the populated ActionsQueue from the Adaptor.
    """

    actions_queue: ActionsQueue
    adaptor: BaseAdaptor

    def __init__(self, actions_queue: ActionsQueue, adaptor: BaseAdaptor) -> None:
        """
        Adaptor Server class in Windows.

        Args:
            actions_queue: A queue used for storing all actions sent by the client.
            adaptor: The adaptor class used for reacting to the request.
        """
        # TODO: Do a code refactoring to generate the namedpipe server path
        #  Need to check if the pipe name is used and the max length.
        self.server_path = rf"\\.\pipe\AdaptorServerNamedPipe_{str(os.getpid())}"
        shutdown_event = Event()
        super().__init__(self.server_path, shutdown_event)

        self.actions_queue = actions_queue
        self.adaptor = adaptor

    def request_handler(
        self, server: NamedPipeServer, pipe_handle: HANDLE
    ) -> ResourceRequestHandler:
        """
        Initializes the handler for handling the request from the client.

        Args:
            server: The NamedPipeServer that maintains the lifecycle of all resources.
            pipe_handle: The pip handle used for communication between client and server.

        Returns:
            ResourceRequestHandler: The Handler that handle the request.
        """
        return WinAdaptorServerResourceRequestHandler(cast("WinAdaptorServer", server), pipe_handle)