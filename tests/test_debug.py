import pytest

try:
    import rich  # noqa

    has_rich = True
except ImportError:
    has_rich = False

from nameko_chassis.debug import debug_state_rich, debug_state_simple
from nameko_chassis.service import ServiceState, WorkerState


@pytest.fixture
def service_state() -> ServiceState:
    worker_state = WorkerState(
        class_name="MyService",
        method_name="my_method",
        args=["spam"],
        kwargs={"answer": "42"},
        data={},
        stacktrace=[],
    )
    return ServiceState(
        version="unknown",
        service_name="my_service",
        uptime=60,
        entrypoints=["my_method"],
        dependencies=["container"],
        running_workers=1,
        max_workers=10,
        worker_states=[worker_state],
    )


def test_debug_state_simple_prints_worker_availability(service_state, capsys) -> None:
    debug_state_simple(service_state)
    captured = capsys.readouterr()
    assert service_state.service_name in captured.out
    assert "Running 1/10 worker threads" in captured.out


@pytest.mark.skipif(not has_rich, reason="rich is not installed")
def test_debug_state_rich_prints_worker_availability(service_state, capsys) -> None:
    debug_state_rich(service_state)
    captured = capsys.readouterr()
    assert service_state.service_name in captured.out
    assert "Running 1/10 worker threads" in captured.out
