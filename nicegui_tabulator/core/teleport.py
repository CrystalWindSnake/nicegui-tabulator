from nicegui.element import Element


class Teleport(Element, component="teleport.js"):
    def __init__(self, to: str) -> None:
        """ """
        super().__init__()
        self._props["to"] = to


teleport = Teleport
