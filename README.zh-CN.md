## NiceGUI Tabulator

这是一个Python包，它通过 [Tabulator](https://github.com/olifolkerd/tabulator) 库提供了一种简单的方式来创建表格。该包构建于 [NiceGUI](https://github.com/zauberzeug/nicegui) 库之上。



<div align="center">

简体中文| [English](./README.md)

</div>

## 功能

- ✅轻松使用 Tabulator 库各种事件、方法
- ✅单元格插槽：可以在单元格中放入任意 nicegui 组件并获得所有功能，而无须编写字符串模板。[示例](#cell-slot)
- ✅内置支持从 pandas 数据创建表格。[示例](#from_pandas)
- 🔲内置支持 excel、pdf 等格式下载
- 🔲行插槽

## 安装

```
pip install nicegui-tabulator
```

## 使用

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
从 pandas 数据创建表格。

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

你可以在创建表格之后立即更新列配置。

```python
tabulator.from_pandas(df).update_column_definition(
    "age", {"hozAlign": "left", "formatter": "progress"}
)
```


### cell-slot

单元格插槽允许你在单元格中放入任意 nicegui 组件并获得所有功能，而无须编写字符串模板。

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
    # 当表格渲染单元格时，会调用这个函数，并传入单元格的属性，包括单元格的值、行索引、列名等信息。
    # props.update_value(new_value) 可以更新单元格的值(只更新服务端，客户端需要手动刷新 `sync_data_to_client`)。
    ui.input(value=props.value, on_change=lambda e: props.update_value(e.value))


@table.add_cell_slot("age")
def _(props: CellSlotProps):
    ui.number(value=props.value, min=0, max=100,on_change=lambda e: props.update_value(e.value))


def print_table_data():
    table.sync_data_to_client()
    table.run_table_method("print", True)


ui.button("print table data", on_click=print_table_data)


```


