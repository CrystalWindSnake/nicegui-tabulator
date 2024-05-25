from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from nicegui.element import Element
from nicegui.awaitable_response import AwaitableResponse
from warnings import warn
from .utils import DeferredTask
from .teleport import teleport
from .types import CellSlotProps

try:
    import pandas as pd
except ImportError:
    pass


class Tabulator(Element, component="tabulator.js", libraries=["libs/tabulator.min.js"]):
    def __init__(
        self,
        options: Dict,
    ) -> None:
        """Create a new tabulator table.

        Args:
            options (Dict): The options for the tabulator table.
        """
        super().__init__()
        self.__deferred_task = DeferredTask()

        self._props["options"] = options
        self.add_resource(Path(__file__).parent / "libs")

        self._cell_slot_map: Dict[str, Callable] = {}
        self._teleport_slots_cache: Dict[Tuple[str, int], teleport] = {}

        def on_update_cell_slot(e):
            field = e.args["field"]
            row_number = e.args["rowNumber"]
            key = (field, row_number)

            if field not in self._cell_slot_map:
                return

            if key in self._teleport_slots_cache:
                tp = self._teleport_slots_cache[key]
                tp.forceUpdate()
            else:
                fn = self._cell_slot_map[field]
                tp = fn(row_number)
                if tp:
                    self._teleport_slots_cache[key] = tp

            self.run_table_method("redraw")

        self.on("updateCellSlot", on_update_cell_slot)

    def delete(self) -> None:
        for tp in self._teleport_slots_cache.values():
            tp.delete()
        return super().delete()

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

        if event.endswith("tableBuilding"):
            warn("The 'tableBuilding' event cannot be triggered.")
            return self

        if not event.startswith("table:"):
            event = f"table:{event}"

        @self.__deferred_task.register
        def _():
            self.run_method("onEvent", event)

        self.on(event, callback)

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

        @self.__deferred_task.register
        def _():
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

        @self.__deferred_task.register
        def _():
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

        @self.__deferred_task.register
        def _():
            self.run_table_method("addColumn", definition, before, position)

    @classmethod
    def from_pandas(
        cls,
        df: "pd.DataFrame",
    ):
        """Create a table from a Pandas DataFrame.

        Note:
        If the DataFrame contains non-serializable columns of type `datetime64[ns]`, `timedelta64[ns]`, `complex128` or `period[M]`,
        they will be converted to strings.

        Args:
            df (pd.DataFrame): The DataFrame to create the table from.
        """

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

        options = {
            "data": df.to_dict(orient="records"),
            "columns": [{"title": col, "field": col} for col in df.columns],
        }

        return cls(options)

    def add_cell_slot(
        self,
        field: str,
    ):
        """
        Add a cell slot to the table.

        @see https://github.com/CrystalWindSnake/nicegui-tabulator?tab=readme-ov-file#cell-slots


        Args:
            field (str): The field name of the column you want to add a cell slot to.


        ## Example Usage

        ```python
        from nicegui import ui
        from nicegui_tabulator import tabulator,CellSlotProps

        table = tabulator({...})

        @table.add_cell_slot("name")
        def name_cell(props: CellSlotProps):
            ui.input(value=props.value, placeholder="Enter name")

        """
        id = f"c{self.id}"

        def wrapper(build_fn: Callable[[CellSlotProps], None]):
            def fn(row_number: int):
                options = self._props["options"]
                data = options.get("data", [])
                if not data:
                    return

                row = data[row_number - 1]

                class_name = f"ng-cell-slot-{field}-{row_number}"
                with teleport(f"#{id} .{class_name}") as tp:
                    cell_slot = CellSlotProps(
                        field=field,
                        value=row[field],
                        row=row,
                        row_number=row_number,
                        table=self,
                    )
                    build_fn(cell_slot)

                return tp

            self.update_column_definition(
                field,
                {
                    ":formatter": rf"""
        function(cell, formatterParams, onRendered){{
            onRendered(function(){{
                const row = cell.getRow();
                const field = cell.getField();
                const rowNumber = row.getIndex();
                const target = cell.getElement();
                target.innerHTML = `<div class="ng-cell-slot-${{field}}-${{rowNumber}} fit"></div>`
                const table = getElement({self.id});
                runMethod(table, 'updateCellSlot',[field,rowNumber]);
            }});
        }}
        """
                },
            )
            self._cell_slot_map[field] = fn

        return wrapper
