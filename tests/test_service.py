import logging

from nameko.testing.services import worker_factory
from nameko_prometheus.dependencies import MetricsServer
from werkzeug.test import EnvironBuilder

from nameko_chassis.service import Service


class MyService(Service):
    name = "my_service"


def test_say_hello():
    service = worker_factory(MyService)
    assert service.say_hello() == "Hello from my_service!"


def test_serve_metrics():
    request = EnvironBuilder(
        method="GET", path="/metrics", headers={"Accept": "text/html"}
    ).get_request()
    # replace metrics mock with a real dependency from nameko-prometheus
    service = worker_factory(MyService, metrics=MetricsServer())
    response = service.serve_metrics(request)
    assert response.status_code == 200


def test_set_log_level():
    service = worker_factory(MyService)
    logger = logging.getLogger("foo.bar")
    logger.setLevel(logging.ERROR)
    service.set_log_level("foo.bar", logging.DEBUG)
    logger = logging.getLogger("foo.bar")
    assert logger.level == logging.DEBUG
