from pathlib import Path
from typing import Callable, Dict, List, Optional
from nicegui.element import Element
from nicegui.events import handle_event
from nicegui import ui, Client as ng_client
from nicegui.awaitable_response import AwaitableResponse
from .events import TabulatorEventArguments

try:
    import pandas as pd
except ImportError:
    pass


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
        """
        Register an event listener for the tabulator table.

        Args:
            event (str): The name of the event to listen for.
            callback (Callable[..., None]): The function to call when the event is triggered.

        """

        @self.__deferred_task.register
        def _():
            self._event_listener_map[event] = callback
            self.run_method("onEvent", event)

        return self

    def run_table_method(
        self, name: str, *args, timeout: float = 1, check_interval: float = 0.01
    ) -> AwaitableResponse:
        """
        Run a method on the tabulator table.

        Args:
            name (str): The name of the method to run.
            *args: The arguments to pass to the method.
            timeout (float, optional): The maximum time to wait for the method to complete. Defaults to 1.
            check_interval (float, optional): The interval at which to check if the method has completed. Defaults to 0.01.

        """
        return self.run_method(
            "run_table_method",
            name,
            *args,
            timeout=timeout,
            check_interval=check_interval,
        )

    def set_columns(self, columns: List[Dict]) -> None:
        """
        To replace the current column definitions for all columns in a table.

        @see https://tabulator.info/docs/6.2/columns#replace

        Args:
            columns (List[Dict]): The list of column definition objects for the table.

        ## Example Usage

        ```python
        table = Tabulator({...})

        new_columns = [
            {'title':"Name", 'field':"name"},
            {'title':"Age", 'field':"age"},
        ]

        table.set_columns(new_columns)
        ```

        """
        self.run_method("setColumns", columns)

    def update_column_definition(self, field: str, definition: Dict) -> None:
        """
        Update an existing column definition.

        @see https://tabulator.info/docs/6.2/columns#update

        Args:
            field (str): The field name of the column you want to update.
            definition (Dict): The new column definition object for the column.

        ## Example Usage
        ```python
        table = Tabulator({...})
        table.update_column_definition("name", {'title':"Updated Title"})
        ```
        """
        self.run_method("updateColumnDefinition", field, definition)

    def add_column(
        self,
        definition: Dict,
        before: Optional[bool] = None,
        position: Optional[str] = None,
    ) -> None:
        """
        Add a column to the table.

        @see https://tabulator.info/docs/6.2/columns#add


        Args:
            definition (Dict): The column definition object for the column you want to add.
            before (Optional[bool], optional): Determines how to position the new column. A value of true will insert the column to the left of existing columns, a value of false will insert it to the right. If a Position argument is supplied then this will determine whether the new colum is inserted before or after this column.
            position (Optional[str], optional): The field to insert the new column next to, this can be any of the standard column component look up options.

        ## Example Usage

        ```python
        table = Tabulator({...})
        table.add_column({'title':"Age", 'field':"age"}, True, "name")
        ```

        """
        self.run_table_method("addColumn", definition, before, position)

    def update(self) -> None:
        super().update()
        self.run_method("update_table")

    @classmethod
    def from_pandas(
        cls,
        df: "pd.DataFrame",
    ):
        def is_special_dtype(dtype):
            return (
                pd.api.types.is_datetime64_any_dtype(dtype)
                or pd.api.types.is_timedelta64_dtype(dtype)
                or pd.api.types.is_complex_dtype(dtype)
                or isinstance(dtype, pd.PeriodDtype)
            )

        special_cols = df.columns[df.dtypes.apply(is_special_dtype)]
        if not special_cols.empty:
            df = df.copy()
            df[special_cols] = df[special_cols].astype(str)

        if isinstance(df.columns, pd.MultiIndex):
            raise ValueError(
                "MultiIndex columns are not supported. "
                "You can convert them to strings using something like "
                '`df.columns = ["_".join(col) for col in df.columns.values]`.'
            )

        return cls(options={"data": df.to_dict(orient="records"), "autoColumns": True})


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
