from nicegui import ui
from .utils.intersection import Intersection
from .utils.module_utils import (
    load_and_execute_module,
    get_page_module_names,
    get_source_code,
)
import sys

sys.path.append(r"e:\working\github\nicegui-tabulator\examples\pages")


ui.context.client.content.classes("items-center")

modules = get_page_module_names()


for module in modules:

    @ui.page(f"/{module}", title=module)
    def _(module=module):
        load_and_execute_module(module, "")


for module in modules:
    with ui.card():
        ui.markdown(f"## {module}")
        iframe = (
            ui.element("iframe").classes("w-[80vw] h-[50vh]").props(f'src="/{module}"')
        )

        with ui.expansion("source code").classes("w-full").props(
            "header-class='outline'"
        ):
            ui.code(get_source_code(module)).classes("w-full")


ui.run(title="Tabulator Example", port=8999)
