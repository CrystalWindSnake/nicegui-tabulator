## NiceGUI Tabulator

This is a Python package that provides a simple way to create tables using the [Tabulator](https://github.com/olifolkerd/tabulator) library. It is built on top of the [NiceGUI](https://github.com/zauberzeug/nicegui) library.


<div align="center">

English| [简体中文](./README.zh-CN.md)

</div>

## Features

- ✅Easily utilize various events and methods from the Tabulator library.
- ✅Built-in themes for Bootstrap 4 and Material Design.[Example](#use_theme)
- ✅Cell Slots: Place any NiceGUI component within a cell and access all its functionalities without writing string templates. [Example](#cell-slot)
- ✅Built-in support for creating tables from pandas data. [Example](#from_pandas)
- 🔲Built-in support for downloading in formats such as Excel, PDF, etc.
- 🔲Row Slots


## Installation

```
pip install nicegui-tabulator
```

## Usage

```python
from nicegui_tabulator import tabulator
from nicegui import ui

tabledata = [
    {"id": 1, "name": "Oli Bob", "age": "12", "col": "red", "dob": ""},
    {"id": 2, "name": "Mary May", "age": "1", "col": "blue", "dob": "14/05/1982"},
    {
        "id": 3,
        "name": "Christine Lobowski",
        "age": "42",
        "col": "green",
        "dob": "22/05/1982",
    },
    {
        "id": 4,
        "name": "Brendon Philips",
        "age": "125",
        "col": "orange",
        "dob": "01/08/1980",
    },
    {
        "id": 5,
        "name": "Margret Marmajuke",
        "age": "16",
        "col": "yellow",
        "dob": "31/01/1999",
    },
]

table_config = {
    "height": 205,  
    "data": tabledata, 
    "columns": [  
        {"title": "Name", "field": "name", "width": 150, "headerFilter": "input"},
        {"title": "Age", "field": "age", "hozAlign": "left", "formatter": "progress"},
        {"title": "Favourite Color", "field": "col"},
        {
            "title": "Date Of Birth",
            "field": "dob",
            "sorter": "date",
            "hozAlign": "center",
        },
    ],
}

table = tabulator(table_config).on_event("rowClick", lambda e: ui.notify(e))


def on_sort():
    table.run_table_method(
        "setSort",
        [
            {"column": "name", "dir": "desc"},
            {"column": "age", "dir": "asc"},
        ],
    )


ui.button("sort", on_click=on_sort)

```

---

## API

### from_pandas
create from pandas dataframe:

```python
from nicegui_tabulator import tabulator
import pandas as pd


df = pd.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "color": ["blue", "red", "green"],
        "dob": [None, "2021-01-01", "2021-02-02"],
    }
)


tabulator.from_pandas(df)
```

---

You can update column configurations immediately after creating the table.


```python
tabulator.from_pandas(df).update_column_definition(
    "age", {"hozAlign": "left", "formatter": "progress"}
)
```


---

### Cell Slot

Cell Slots allow you to place any NiceGUI component within a cell and access all its functionalities without writing string templates.

```python
from nicegui import ui
from nicegui_tabulator import tabulator, CellSlotProps


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

table = tabulator(table_config)


@table.add_cell_slot("name")
def _(props: CellSlotProps):
    # This function is called when rendering the cell of the table, and it receives the properties of the cell,
    # including the value of the cell, row index, column name, etc.
    # props.update_value(new_value) can update the value of the cell (updates server-side only, the client needs to manually refresh `sync_data_to_client`).
    ui.input(value=props.value, on_change=lambda e: props.update_value(e.value))


@table.add_cell_slot("age")
def _(props: CellSlotProps):
    ui.number(value=props.value, min=0, max=100,on_change=lambda e: props.update_value(e.value))


def print_table_data():
    table.sync_data_to_client()
    table.run_table_method("print", True)

ui.button("print table data", on_click=print_table_data)
```

---

### use_theme

```python
from nicegui_tabulator import tabulator, use_theme

# use the theme for all clients
use_theme('bootstrap4')

# use the theme only for the current client
use_theme('bootstrap4', shared=False)

@ui.page('/')
def my_page():
    # use the theme only for this page
    use_theme('bootstrap4')
```


### Dates & Times (Luxon)

Tabulator’s date/time features (e.g. `formatter: "datetime"`, `sorter: "date"` or `sorter: "datetime"`)
require **Luxon**. `nicegui-tabulator` does not bundle Luxon; enable it explicitly:

```python
from nicegui import ui
from nicegui_tabulator import tabulator, import_luxon_dependency

# Inject Luxon before creating tables that use date/time formatting/sorting
import_luxon_dependency(shared=True)  # (app-wide)

tabledata = [
    {"id": 1, "name": "Oli Bob", "dob": "1982-05-14"},
    {"id": 2, "name": "Mary May", "dob": "1999-01-31"},
]

table_config = {
    "layout": "fitColumns",
    "data": tabledata,
    "columns": [
        {"title": "Name", "field": "name"},
        {
            "title": "Date Of Birth",
            "field": "dob",
            "formatter": "datetime",
            "formatterParams": {"inputFormat": "iso", "outputFormat": "dd/MM/yyyy"},
            "sorter": "date",
            "sorterParams": {"format": "iso"},
        },
    ],
}

tabulator(table_config)
ui.run()
