from pathlib import Path
from typing import Callable, Dict
from nicegui.element import Element
from nicegui.events import handle_event
from nicegui import ui, Client as ng_client
from nicegui.awaitable_response import AwaitableResponse
from .events import TabulatorEventArguments


class Tabulator(Element, component="tabulator.js", libraries=["libs/tabulator.min.js"]):
    def __init__(
        self,
        options: Dict,
    ) -> None:
        super().__init__()
        self.__deferred_task = DeferredTask()
        self._event_listener_map: Dict[str, Callable[..., None]] = {}

        self._props["options"] = options
        self.add_resource(Path(__file__).parent / "libs")

        def on_table_event(e):
            event_name = e.args["eventName"]

            event_args = TabulatorEventArguments(
                sender=self, client=self.client, args=e.args["args"]
            )

            if event_name in self._event_listener_map:
                handle_event(self._event_listener_map[event_name], event_args)

        self.on("table-event", on_table_event)

    def on_event(
        self,
        event: str,
        callback: Callable[..., None],
    ):
        """ """

        @self.__deferred_task.register
        def _():
            self._event_listener_map[event] = callback
            self.run_method("onEvent", event)

        return self

    def run_table_method(
        self, name: str, *args, timeout: float = 1, check_interval: float = 0.01
    ) -> AwaitableResponse:
        """ """
        return self.run_method(
            "run_table_method",
            name,
            *args,
            timeout=timeout,
            check_interval=check_interval,
        )


class DeferredTask:
    def __init__(self):
        self._tasks = []

        async def on_client_connect(
            client: ng_client,
        ):
            await client.connected()

            for task in self._tasks:
                task()

            # Avoid events becoming ineffective due to page refresh when sharing the client.
            if not client.shared:
                client.connect_handlers.remove(on_client_connect)  # type: ignore

        ui.context.client.on_connect(on_client_connect)

    def register(self, task: Callable[..., None]):
        if ui.context.client.has_socket_connection:
            task()
        else:
            self._tasks.append(task)
