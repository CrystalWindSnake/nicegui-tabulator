from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from typing import Any, Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tabulator import Tabulator


@dataclass
class CellSlotProps:
    field: str
    value: Any
    row: Dict
    row_number: int
    table: Tabulator = dc_field(init=True, repr=False)

    def update_value(self, value):
        id = self.row["id"]

        options = self.table._props["options"]
        data = options["data"]

        data[self.row_number - 1].update({self.field: value})

        # self.table.run_table_method("updateData", [{"id": id, self.field: value}])
