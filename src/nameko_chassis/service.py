from __future__ import annotations

import os
import time
import traceback
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from nameko.containers import ServiceContainer
from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko.web.handlers import http
from nameko_prometheus import PrometheusMetrics
from nameko_sentry import SentryReporter
from nameko_zipkin import Zipkin
from werkzeug.wrappers import Request, Response

from .dependencies import ContainerProvider, SentryLoggerConfig

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

    SentryLoggerConfig()
    sentry = SentryReporter()
    config = Config()
    container = ContainerProvider()
    zipkin = Zipkin()
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
