from __future__ import annotations

import logging
import os
import socket
import time
import traceback
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from nameko.containers import ServiceContainer
from nameko.rpc import rpc
from nameko.web.handlers import http
from nameko_prometheus import PrometheusMetrics
from werkzeug.wrappers import Request, Response

from .dependencies import ContainerProvider

START_TIME = time.time()


@dataclass(frozen=True)
class WorkerState:
    """
    Attributes of a single running worker greenthread.
    """

    class_name: str
    method_name: str
    args: List[str]
    kwargs: Dict[str, str]
    data: Dict[str, str]
    stacktrace: List[str]


@dataclass(frozen=True)
class ServiceState:
    """
    Introspection result for an entire service, including running workers.
    """

    version: str
    service_name: str
    uptime: float
    entrypoints: List[str]
    dependencies: List[str]
    running_workers: int
    max_workers: int
    worker_states: List[WorkerState]

    @classmethod
    def from_container(cls, container: ServiceContainer) -> ServiceState:
        """
        Introspects a service container and its workers to build ServiceState.
        """
        worker_states = [
            WorkerState(
                class_name=container.service_cls.__name__,
                method_name=ctx.entrypoint.method_name,
                # as long as we don't need to do anything else than preview
                # the args/kwargs, let's dump them as strings; asdict()
                # has trouble with less simple argument types such as Request
                args=[str(arg) for arg in ctx.args],
                kwargs={k: str(v) for k, v in ctx.kwargs.items()},
                data={k: str(v) for k, v in ctx.context_data.items()},
                # format greenthread's stack trace as list of lines
                stacktrace=traceback.format_list(
                    traceback.extract_stack(thread.gr_frame)
                ),
            )
            for ctx, thread in container._worker_threads.items()
        ]
        return ServiceState(
            version=os.environ.get("APP_VERSION", "unknown"),
            service_name=container.service_name,
            uptime=time.time() - START_TIME,
            entrypoints=[e.method_name for e in container.entrypoints],
            dependencies=[d.attr_name for d in container.dependencies],
            running_workers=len(container._worker_threads),
            max_workers=container.max_workers,
            worker_states=worker_states,
        )


class Service:
    """
    Base class for nameko services.
    """

    name = "no name"

    container = ContainerProvider()
    metrics = PrometheusMetrics()

    @rpc
    def say_hello(self) -> str:
        """
        RPC method to ping the service to check if it can be reached.
        """
        return f"Hello from {self.name}!"

    @rpc
    def query_state(self) -> Dict[str, Any]:
        """
        Returns a detailed state of running service.
        """
        return asdict(ServiceState.from_container(self.container))

    @http("GET", "/metrics")
    def serve_metrics(self, request: Request) -> Response:
        """
        Exposes Prometheus metrics over HTTP.
        """
        return self.metrics.expose_metrics(request)

    @rpc
    def set_log_level(self, logger_name: str, level: int) -> str:
        """
        Temporarily override log level in a running service.

        Useful for example for debugging a live service instance, where your
        default log level is INFO or higher to avoid clutter in logs. This
        RPC allows you to change log level while the application is running.

        For example::

            >>> n.rpc.my_service.set_log_level("some.module", logging.DEBUG)

        Now your logs will include debug messages from ``some.module`` even if
        your static log configuration (dictConfig etc.) silenced them.

        Caveat #1: Updating log level in this manner will only affect loggers
        acquired *after* this RPC call. So your code must call
        ``logging.get_logger()`` as late as possible. This unfortunately means
        that library code may or may not be affected - depends on how the
        library acquires its loggers.

        Caveat #2: If your service runs in multiple replicas behind a load
        balancer, you must call this RPC method at least as many times as
        there are replicas to ensure that each replica will have its log level
        changed.
        """
        logger = logging.getLogger(__name__)
        logger_to_change = logging.getLogger(logger_name)
        logger.info(
            f"Updating level for {logger_name} from {logger_to_change.level} to {level}"
        )
        message = f"""
        Log level changed on host {socket.gethostname()}. Revert with:

            n.rpc.{self.name}.set_log_level({logger_name!r}, {logger_to_change.level!r})
        """
        logger_to_change.setLevel(level)
        return message
