from datetime import datetime, timedelta, timezone
from nicegui import ui
from .screen import BrowserManager
from playwright.sync_api import expect, Locator
from nicegui_tabulator import tabulator
import pandas as pd


def get_table_data(table: Locator):
    rows = table.locator(".tabulator-row").all()
    return [row.locator(".tabulator-cell").all_text_contents() for row in rows]


def test_base(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        tabledata = [
            {"id": 1, "name": "Oli Bob", "age": "12", "col": "red", "dob": ""},
            {
                "id": 2,
                "name": "Mary May",
                "age": "1",
                "col": "blue",
                "dob": "14/05/1982",
            },
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
                {
                    "title": "Name",
                    "field": "name",
                    "width": 150,
                    "headerFilter": "input",
                },
                {
                    "title": "Age",
                    "field": "age",
                    "hozAlign": "left",
                    "formatter": "progress",
                },
                {"title": "Favourite Color", "field": "col"},
                {
                    "title": "Date Of Birth",
                    "field": "dob",
                    "sorter": "date",
                    "hozAlign": "center",
                },
            ],
        }

        table = (
            tabulator(table_config)
            .classes("target")
            .on_event(
                "rowClick", lambda e: lbl_row_click.set_text(str(e.args["row"]["name"]))
            )
        )

        lbl_row_click = ui.label("").classes("row-click-label")

        def on_sort():
            table.run_table_method(
                "setSort",
                [
                    {"column": "name", "dir": "desc"},
                    {"column": "age", "dir": "asc"},
                ],
            )

        ui.button("sort", on_click=on_sort).classes("sort-button")

    page = browser.open(page_path)
    page.wait_for_timeout(600)

    table = page.locator(".target")
    lbl_row_click = page.locator(".row-click-label")

    expect(table).to_be_visible()

    data = get_table_data(table)

    assert data[0] == ["Oli Bob", "", "red", "\xa0"]

    # sort by name
    page.get_by_role("button", name="sort").click()

    expect(
        table.locator(".tabulator-row").first.locator(".tabulator-cell").first
    ).to_contain_text("Mary May")

    # click row
    table.locator(".tabulator-row").first.click()
    expect(lbl_row_click).to_contain_text("Mary May")


def test_manipulate_columns(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        tabledata = [
            {"id": 1, "name": "Oli Bob", "age": "12", "color": "red", "dob": ""},
            {
                "id": 2,
                "name": "Mary May",
                "age": "1",
                "color": "blue",
                "dob": "14/05/1982",
            },
        ]

        table_config = {
            "height": 205,
            "data": tabledata,
            "columns": [
                {"title": "Name", "field": "name", "width": 150},
                {"title": "Age", "field": "age", "hozAlign": "left"},
            ],
        }

        table = tabulator(table_config).classes("target")

        def update_columns():
            table.update_column_definition(
                "name",
                {
                    "title": "new name",
                },
            )

        ui.button("update_columns", on_click=update_columns)

        def set_columns():
            table.set_columns(
                [
                    {"title": "color", "field": "color"},
                    {"title": "dob", "field": "dob"},
                ]
            )

        ui.button("set_columns", on_click=set_columns)

        def add_column():
            table.add_column({"title": "Age", "field": "age"}, False, "color")

        ui.button("add_column", on_click=add_column)

    page = browser.open(page_path)

    table = page.locator(".target")

    # update column
    page.get_by_role("button", name="update_columns").click()
    expect(table.locator(".tabulator-headers .tabulator-col").first).to_contain_text(
        "new name"
    )

    # set columns
    page.get_by_role("button", name="set_columns").click()
    expect(table.locator(".tabulator-headers .tabulator-col").first).to_contain_text(
        "color"
    )
    expect(table.locator(".tabulator-headers .tabulator-col").last).to_contain_text(
        "dob"
    )

    # add column
    page.get_by_role("button", name="add_column").click()
    expect(table.locator(".tabulator-headers .tabulator-col").nth(1)).to_contain_text(
        "Age"
    )


def test_columns_method_immediately(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        tabledata = [
            {"id": 1, "name": "Alice", "age": "12"},
        ]

        table_config = {
            "height": 205,
            "data": tabledata,
            "columns": [
                {"title": "Name", "field": "name"},
                {"title": "Age", "field": "age"},
            ],
        }

        tabulator(table_config).classes("target").update_column_definition(
            "name",
            {
                "title": "new name",
            },
        )

    page = browser.open(page_path)
    body_expect = expect(page.locator("body"))
    body_expect.to_contain_text("new name")


def test_dynamic_configs(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        tabledata = [
            {"id": 1, "name": "Oli Bob", "age": "12", "color": "red", "dob": ""}
        ]

        table_config = {
            "height": 205,
            "data": tabledata,
            "columns": [
                {
                    "title": "Name",
                    "field": "name",
                    "width": 150,
                    ":cellClick": 'function(e, cell){emitEvent("cellClick","name")}',
                },
                {"title": "Age", "field": "age", "hozAlign": "left"},
            ],
        }

        ui.on("cellClick", lambda e: lbl_cell_click.set_text(e.args))

        tabulator(table_config).classes("target")

        lbl_cell_click = ui.label().classes("cell-click-label")

    page = browser.open(page_path)

    table = page.locator(".target")
    lbl_cell_click = page.locator(".cell-click-label")

    table.locator(".tabulator-row .tabulator-cell").first.click()

    expect(lbl_cell_click).to_contain_text("name")


def test_from_pandas(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        df = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "color": ["blue", "red", "green"],
                "dob": [None, "2021-01-01", "2021-02-02"],
            }
        )

        tabulator.from_pandas(df).classes("target")

    page = browser.open(page_path)

    table = page.locator(".target")
    data = get_table_data(table)

    assert data[0] == ["Alice", "25", "blue", "\xa0"]


def test_problematic_datatypes(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        df = pd.DataFrame(
            {
                "Datetime_col": [datetime(2020, 1, 1)],
                "Datetime_col_tz": [datetime(2020, 1, 1, tzinfo=timezone.utc)],
                "Timedelta_col": [timedelta(days=5)],
                "Complex_col": [1 + 2j],
                "Period_col": pd.Series([pd.Period("2021-01")]),
            }
        )

        tabulator.from_pandas(df)

    page = browser.open(page_path)

    body_expect = expect(page.locator("body"))
    body_expect.to_contain_text("Datetime_col")
    body_expect.to_contain_text("Datetime_col_tz")
    body_expect.to_contain_text("Timedelta_col")
    body_expect.to_contain_text("Complex_col")
    body_expect.to_contain_text("Period_col")
