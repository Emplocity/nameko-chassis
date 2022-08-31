import pytest
from nameko import config
from nameko.rpc import RpcProxy, rpc
from nameko.testing.services import entrypoint_hook

from nameko_chassis.health import is_service_responsive


@pytest.fixture(autouse=True)
def rabbit_config():
    with config.patch({"AMQP_URI": "pyamqp://localhost:5672"}):
        yield


class MyService:
    name = "my_service"
    my_service = RpcProxy(name)

    @rpc
    def up(self):
        return "ok"

    @rpc
    def is_responsive(self):
        return is_service_responsive(self.my_service, method_name="up")


def test_is_service_responsive(container_factory):
    container = container_factory(MyService)
    container.start()
    with entrypoint_hook(container, "is_responsive") as hook:
        assert hook() is True
