from nicegui_tabulator import tabulator, use_theme, CellSlotProps
from nicegui import ui

use_theme("semanticui", shared=False)


chart_data = {
    "bar": [
        {"type": "bar", "name": "Alpha", "data": [0.1, 0.2]},
        {"type": "bar", "name": "Beta", "data": [0.3, 0.4]},
    ],
    "foo": [
        {"type": "bar", "name": "Alpha", "data": [20, 50]},
        {"type": "bar", "name": "Beta", "data": [39, 20]},
    ],
}

tabledata = [
    {"id": 1, "name": "bar", "age": "12", "chart": None},
    {"id": 2, "name": "foo", "age": "1", "chart": None},
]

table_config = {
    "data": tabledata,
    "layout": "fitDataStretch",
    "columnDefaults": {"vertAlign": "middle"},
    "columns": [
        {"title": "Name", "field": "name"},
        {"title": "Age", "field": "age"},
        {"title": "Chart", "field": "chart", "widthGrow": 1},
    ],
    "printConfig": {
        "formatCells": False,
    },
}


table = tabulator(table_config)


@table.add_cell_slot("name")
def _(props: CellSlotProps):
    def on_blur():
        props.update_to_client()

    ui.input(value=props.value, on_change=lambda e: props.update_value(e.value)).on(
        "blur", on_blur
    )


@table.add_cell_slot("chart")
def _(props: CellSlotProps):
    series_data = chart_data[props.row["name"]]

    ui.echart(
        {
            "xAxis": {"type": "value"},
            "yAxis": {"type": "category", "data": ["A", "B"], "inverse": True},
            "legend": {"textStyle": {"color": "gray"}},
            "series": series_data,
        }
    )


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
