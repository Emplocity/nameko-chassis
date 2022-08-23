import logging

import pytest
from nameko import config
from nameko.testing.services import entrypoint_hook
from nameko_prometheus.utils import reset_prometheus_registry
from werkzeug.test import EnvironBuilder

from nameko_chassis.service import Service


@pytest.fixture(autouse=True)
def rabbit_config():
    with config.patch({"AMQP_URI": "pyamqp://localhost:5672"}):
        yield


@pytest.fixture(autouse=True)
def reset_registry():
    reset_prometheus_registry("my_service")


class MyService(Service):
    name = "my_service"


def test_say_hello(container_factory):
    container = container_factory(MyService)
    container.start()
    with entrypoint_hook(container, "say_hello") as hook:
        assert hook() == "Hello from my_service!"


def test_serve_metrics(container_factory):
    request = EnvironBuilder(
        method="GET", path="/metrics", headers={"Accept": "text/html"}
    ).get_request()
    container = container_factory(MyService)
    container.start()
    with entrypoint_hook(container, "serve_metrics") as hook:
        response = hook(request)
        assert response.status_code == 200


def test_set_log_level(container_factory):
    container = container_factory(MyService)
    container.start()
    logger = logging.getLogger("foo.bar")
    logger.setLevel(logging.ERROR)
    with entrypoint_hook(container, "set_log_level") as hook:
        hook("foo.bar", logging.DEBUG)
    logger = logging.getLogger("foo.bar")
    assert logger.level == logging.DEBUG
