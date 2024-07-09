from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from typing import Any, Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tabulator import Tabulator


@dataclass
class CellSlotProps:
    field: str
    """The name of the field in the row data."""
    value: Any
    """The value of the field in the row data."""
    row: Dict
    """The row data."""
    row_number: int
    """The position(starting from 1) of the row in the table data."""
    table: Tabulator = dc_field(init=True, repr=False)
    """The parent Tabulator instance."""

    def update_value(self, value):
        """Updates the value of the field in the row data only on the server side."""
        index_field = self.table.index_field
        data = [{index_field: self.row[index_field], self.field: value}]
        self.table._update_data_on_server(data)

    def update_to_client(self):
        """Updates the value of the field in the row data on the client side."""

        index_field = self.table.index_field
        data = [{index_field: self.row[index_field], self.field: self.row[self.field]}]
        self.table.run_table_method(
            "updateData",
            data,
        )
