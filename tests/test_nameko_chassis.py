from nameko.testing.services import worker_factory

from nameko_chassis.service import Service


class MyService(Service):
    name = "my_service"


def test_say_hello():
    service = worker_factory(MyService)
    assert service.say_hello() == "Hello from my_service!"
