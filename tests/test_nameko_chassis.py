from unittest.mock import create_autospec

from nameko.testing.services import worker_factory
from nameko_prometheus.dependencies import MetricsServer
from werkzeug.wrappers import Request

from nameko_chassis.service import Service


class MyService(Service):
    name = "my_service"


def test_say_hello():
    service = worker_factory(MyService)
    assert service.say_hello() == "Hello from my_service!"


def test_serve_metrics():
    request = create_autospec(Request)
    # replace metrics mock with a real dependency from nameko-prometheus
    service = worker_factory(MyService, metrics=MetricsServer())
    response = service.serve_metrics(request)
    assert response.status_code == 200
