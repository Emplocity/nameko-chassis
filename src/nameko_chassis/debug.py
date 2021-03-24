import textwrap
from typing import List

try:
    import rich  # noqa
    from rich.columns import Columns  # noqa
    from rich.console import RenderableType  # noqa
    from rich.panel import Panel  # noqa

    has_rich = True
except ImportError:
    has_rich = False

from .service import ServiceState


def debug_runner(runner):
    """
    Dump debug information about service state to standard output.

    Call this method from within nameko backdoor which exposes a ``runner``
    local variable.

    If rich_ is available, the output will be way prettier than you'd expect :)

    .. _rich: https://github.com/willmcgugan/rich
    """
    func = debug_state_rich if has_rich else debug_state_simple
    for container in runner.containers:
        service_state = ServiceState.from_container(container)
        func(service_state)


def debug_state_simple(state: ServiceState) -> None:
    """
    Print service state to stdout with some rudimentary formatting.
    """
    print(
        f"Container for service '{state.service_name}' with {len(state.entrypoints)} entrypoints and {len(state.dependencies)} dependencies"
    )
    print(f"Running {state.running_workers}/{state.max_workers} worker threads:")
    for i, worker_state in enumerate(state.worker_states):
        print(
            textwrap.dedent(
                f"""
            ------------
            Thread #{i}: {worker_state.class_name}.{worker_state.method_name}
            Args: {worker_state.args}
            Kwargs: {worker_state.kwargs}
            Context data: {worker_state.data}
            """
            )
        )
        print("".join(worker_state.stacktrace))


def debug_state_rich(state: ServiceState) -> None:
    """
    Pretty-print service state using rich.
    """
    renderables: List[RenderableType] = [
        f"""{len(state.entrypoints)} entrypoints
{len(state.dependencies)} dependencies
Running {state.running_workers}/{state.max_workers} worker threads"""
    ]
    for i, worker_state in enumerate(state.worker_states):
        formatted_stack = "".join(
            f"[bold]{line}[/bold]"
            if "site-packages" not in line
            else f"[dim]{line}[/dim]"
            for line in worker_state.stacktrace
        )
        renderables.append(
            Panel(
                f"""
Args: {worker_state.args}
Kwargs: {worker_state.kwargs}
Context data: {worker_state.data}

Traceback:
{formatted_stack}""",
                title=f"Thread #{i}: [magenta]{worker_state.class_name}.{worker_state.method_name}[/magenta]",
            )
        )
    rich.print(Panel(Columns(renderables), title=f"[bold]{state.service_name}[/bold]"))
