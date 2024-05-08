from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
)

from nicegui.events import UiEventArguments
from nicegui.dataclasses import KWONLY_SLOTS


@dataclass(**KWONLY_SLOTS)
class TabulatorEventArguments(UiEventArguments):
    args: Any
