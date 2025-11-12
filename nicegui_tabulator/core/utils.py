from typing import Callable
from nicegui import ui, Client as ng_client
import uuid


class DeferredTask:
    def __init__(self):
        self._tasks = []
        self.component_connected = False

        async def on_client_connect(
            client: ng_client,
        ):
            await client.connected()

            self.flush()

        ui.context.client.on_connect(on_client_connect)

    def register(self, task: Callable[..., None]):
        if ui.context.client.has_socket_connection and self.component_connected:
            task()
        else:
            self._tasks.append(task)

    def flush(self):
        for task in self._tasks:
            task()

        self._tasks.clear()


def generate_dataframe_unique_id_column_name():
    return f"__{uuid.uuid4().hex}"
