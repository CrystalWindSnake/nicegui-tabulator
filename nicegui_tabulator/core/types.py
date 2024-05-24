from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CellSlotProps:
    field: str
    value: Any
    row: Dict
    row_number: int
