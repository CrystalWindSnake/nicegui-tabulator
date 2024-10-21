from nicegui_tabulator import tabulator
from nicegui import ui

tabledata = [
    {
        "id": 1,
        "name": "Oli Bob",
        "age": "12",
    },
    {
        "id": 2,
        "name": "Mary May",
        "age": "1",
    },
    {
        "id": 3,
        "name": "Christine Lobowski",
        "age": "42",
    },
]

table_config = {
    "height": 205,
    "data": tabledata,
    "rowHeader": {
        "formatter": "rowSelection",
        "titleFormatter": "rowSelection",
    },
    "columns": [
        {
            "title": "Name",
            "field": "name",
        },
        {
            "title": "Age",
            "field": "age",
        },
    ],
}


table = tabulator(table_config)


async def get_rows():
    rows = await table.get_selected_data()
    ui.notify(rows)


ui.button("Get Selected Rows", on_click=get_rows)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
