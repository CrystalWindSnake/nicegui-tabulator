from typing import Callable, List, Union
import asyncio
import uuid

from nicegui import ui, Client as ng_client
from nicegui.awaitable_response import AwaitableResponse

_TTask = Union[Callable[..., None], Callable[..., AwaitableResponse]]


class DeferredTask:
    def __init__(self):
        self._tasks: List[_TTask] = []
        self.component_connected = False

        async def on_client_connect(
            client: ng_client,
        ):
            await client.connected()

            self.flush()

        ui.context.client.on_connect(on_client_connect)

    def register(self, task: _TTask):
        if ui.context.client.has_socket_connection and self.component_connected:
            task()
        else:
            self._tasks.append(task)

    def flush(self):
        for task in self._tasks:
            self._execute_task(task)

        self._tasks.clear()

    def _execute_task(self, task: _TTask) -> None:
        result = task()
        if asyncio.iscoroutine(result):
            asyncio.create_task(result)


def generate_dataframe_unique_id_column_name() -> str:
    return f"__{uuid.uuid4().hex}"
