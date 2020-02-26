from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko.web.handlers import http
from nameko_prometheus import PrometheusMetrics
from nameko_sentry import SentryReporter
from nameko_zipkin import Zipkin
from werkzeug.wrappers import Request, Response

from .dependencies import SentryLoggerConfig


class Service:
    """
    Base class for nameko services.
    """

    name = "no name"

    SentryLoggerConfig()
    sentry = SentryReporter()
    config = Config()
    zipkin = Zipkin()
    metrics = PrometheusMetrics()

    @rpc
    def say_hello(self) -> str:
        """
        RPC method to ping the service to check if it can be reached.
        """
        return f"Hello from {self.name}!"

    @http("GET", "/metrics")
    def serve_metrics(self, request: Request) -> Response:
        """
        Exposes Prometheus metrics over HTTP.
        """
        return self.metrics.expose_metrics(request)
