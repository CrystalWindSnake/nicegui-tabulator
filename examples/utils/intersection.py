from typing import Any, Optional, Callable
from nicegui import ui
from nicegui.events import UiEventArguments, GenericEventArguments, handle_event
from nicegui.dataclasses import KWONLY_SLOTS

from dataclasses import dataclass


@dataclass(**KWONLY_SLOTS)
class VisibilityEventArguments(UiEventArguments):
    value: bool


class Intersection(ui.element):
    def __init__(
        self,
        *,
        once: bool = False,
        on_visibility: Optional[Callable[..., Any]] = None,
    ) -> None:
        """Intersection Quasar element

        Args:
            on_visibility (Optional[Callable[..., Any]], optional): _description_. Defaults to None.
        """
        super().__init__("q-intersection")

        self._props["once"] = once

        if on_visibility:
            self.on_visibility(on_visibility)

    def on_visibility(self, callback: Callable[..., Any]):
        def handle_visibility(e: GenericEventArguments) -> None:
            handle_event(
                callback,
                VisibilityEventArguments(
                    sender=self,
                    client=self.client,
                    value=e.args,
                ),
            )

        return self.on("visibility", handle_visibility)
