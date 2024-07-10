from nicegui_tabulator import tabulator, use_theme
from nicegui import ui

use_theme("semanticui", shared=False)


tabledata = [
    {"id": 1, "name": "bar", "age": "12"},
    {"id": 2, "name": "foo", "age": "1"},
]

table_config = {
    "data": tabledata,
    "columns": [
        {"title": "Name", "field": "name"},
        {"title": "Age", "field": "age"},
    ],
    "printConfig": {
        "formatCells": False,
    },
}


def select_theme():
    use_theme(theme.value or "default", shared=False)


theme = ui.toggle(
    [
        "default",
        "bootstrap3",
        "bootstrap4",
        "bootstrap5",
        "bulma",
        "materialize",
        "midnight",
        "modern",
        "semanticui",
        "simple",
        "site",
        "site_dark",
    ],
    value="semanticui",
    on_change=select_theme,
).props("no-caps")

tabulator(table_config)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
