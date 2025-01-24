from datetime import datetime, timedelta, timezone
import re
from typing import Dict, List, Optional
from nicegui import ui
from .screen import BrowserManager
from playwright.sync_api import expect, Locator, Page
from nicegui_tabulator import tabulator, CellSlotProps
import pandas as pd


def get_table_data(table: Locator):
    rows = table.locator(".tabulator-row").all()
    return [row.locator(".tabulator-cell").all_text_contents() for row in rows]


def check_table_rows(table: Locator, expected_data: List[List]):
    rows = table.locator(".tabulator-row")
    expect(rows).to_have_count(len(expected_data))

    for i, data_row in enumerate(expected_data):
        row = rows.nth(i)
        expect(row).to_contain_text("".join(data_row))


def create_table_options(data: Optional[List[Dict]] = None):
    tabledata = data or [
        {"id": 1, "name": "bar", "age": "12"},
        {"id": 2, "name": "foo", "age": "1"},
    ]

    table_config = {
        "data": tabledata,
        "columns": [
            {"title": "Name", "field": "name"},
            {"title": "Age", "field": "age"},
        ],
    }

    return table_config


class ServerDataChecker:
    def __init__(
        self,
        server_classes="server-data",
        client_classes="client-data",
        show_client_data_btn_class="show-client-data",
        show_server_data_btn_class="show-server-data",
    ):
        self.server_classes = server_classes
        self.client_classes = client_classes
        self.show_client_data_btn_class = show_client_data_btn_class
        self.show_server_data_btn_class = show_server_data_btn_class

    def create_elements(self, table: tabulator, server_data_button=False):
        label_server_data = ui.label("").classes(self.server_classes)
        text_client_data = ui.label("").classes(self.client_classes)

        async def show_client_data():
            data = await table.run_table_method("getData")
            text_client_data.set_text(str(data))

        ui.button("show client data", on_click=show_client_data).classes(
            self.show_client_data_btn_class
        )

        if server_data_button:

            def show_server_data():
                label_server_data.set_text(str(table.data))

            ui.button("show server data", on_click=show_server_data).classes(
                self.show_server_data_btn_class
            )

        return label_server_data

    def expect_server_data(self, page: Page):
        server = page.locator(f".{self.server_classes}")
        client = page.locator(f".{self.client_classes}")
        page.locator(f".{self.show_client_data_btn_class}").click()
        expect(server).to_contain_text(client.inner_text())


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
            .on_event("tableBuilt", lambda e: lbl_table_built.set_text("Table Built"))
        )

        lbl_row_click = ui.label("").classes("row-click-label")
        lbl_table_built = ui.label("").classes("table-built-label")

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

    table = page.locator(".target")
    lbl_row_click = page.locator(".row-click-label")
    lbl_table_built = page.locator(".table-built-label")

    expect(table).to_be_visible()
    expect(lbl_table_built).to_contain_text("Table Built")

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


def test_from_pandas_column_definition(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        df = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie"],
            }
        )

        def col_def(col_name: str):
            return {
                "title": f"new {col_name}",
            }

        tabulator.from_pandas(
            df,
            column_definition=col_def,
        ).classes("target")

    page = browser.open(page_path)
    body_expect = expect(page.locator("body"))
    body_expect.to_contain_text("new name")


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


def test_cell_slot(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
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
        }

        table = tabulator(table_config).classes("target")

        @table.add_cell_slot("name")
        def _(props: CellSlotProps):
            ui.input(value=props.value, on_change=lambda e: props.update_value(e.value))

        @table.add_cell_slot("age")
        def _(props: CellSlotProps):
            ui.number(value=props.value, min=0, max=100)

        lbl_opts = ui.label("").classes("table-options")

        def update_options_to_label():
            lbl_opts.set_text(str(table._props["options"]["data"][0]))

        ui.button("update options to label", on_click=update_options_to_label)

    page = browser.open(page_path)
    table_locator = page.locator(".target")
    first_name_input = table_locator.get_by_role("textbox").first

    table_expect = expect(table_locator)

    table_expect.to_be_visible()

    expect(first_name_input).to_have_value("bar")

    # client options
    first_name_input.fill("new bar")
    page.get_by_role("button").filter(has_text="update options to label").click()
    expect(page.locator(".table-options")).to_contain_text(
        """{'id': 1, 'name': 'new bar', 'age': '12'}"""
    )


def test_cell_slot_update_data_by_code(browser: BrowserManager, page_path: str):
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table_config = create_table_options()

        table = tabulator(table_config).classes("target")
        server_data_checker.create_elements(table, server_data_button=True)

        @table.add_cell_slot("name")
        def _(props: CellSlotProps):
            def on_blur():
                props.update_to_client()

            ui.input(
                value=props.value, on_change=lambda e: props.update_value(e.value)
            ).on("blur", on_blur)

        def change_data():
            table.update_data([{"id": 1, "name": "change by code"}])

        ui.button("change data", on_click=change_data).classes("change-data")

    page = browser.open(page_path)
    table_locator = page.locator(".target")
    btn_change_data = page.locator(".change-data")
    btn_show_client_data = page.locator(
        f".{server_data_checker.show_client_data_btn_class}"
    )
    btn_show_server_data = page.locator(
        f".{server_data_checker.show_server_data_btn_class}"
    )

    first_name_input = table_locator.get_by_role("textbox").first

    first_name_input.fill("new bar")
    expect(first_name_input).to_have_value("new bar")

    btn_show_client_data.click()
    btn_show_server_data.click()

    server_data_checker.expect_server_data(page)

    # change data by code
    btn_change_data.click()
    btn_show_client_data.click()
    btn_show_server_data.click()

    expect(first_name_input).to_have_value("change by code")
    server_data_checker.expect_server_data(page)

    # change data again
    first_name_input.fill("new bar")
    expect(first_name_input).to_have_value("new bar")
    server_data_checker.expect_server_data(page)

    # change data by code again
    btn_change_data.click()
    btn_show_client_data.click()
    btn_show_server_data.click()

    expect(first_name_input).to_have_value("change by code")
    server_data_checker.expect_server_data(page)


def test_cell_slot_with_pagination(browser: BrowserManager, page_path: str):
    @ui.page(page_path)
    def _():
        tabledata = [
            {"id": 1, "name": "name1", "age": "10"},
            {"id": 2, "name": "name2", "age": "20"},
            {"id": 3, "name": "target name in page2", "age": "30"},
        ]

        table_config = {
            "data": tabledata,
            "columns": [
                {"title": "Name", "field": "name"},
                {"title": "Age", "field": "age"},
            ],
            "pagination": True,
            "paginationSize": 2,
        }

        table = tabulator(table_config).classes("target")

        @table.add_cell_slot("name")
        def _(props: CellSlotProps):
            ui.label(props.value)

        lbl_opts = ui.label("").classes("table-options")

        def update_options_to_label():
            lbl_opts.set_text(str(table._props["options"]["data"][0]))

        ui.button("update options to label", on_click=update_options_to_label)

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    page.get_by_label("Show Page 2").click()
    expect(table_locator).to_contain_text("target name in page2")


def test_set_data(browser: BrowserManager, page_path: str):
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(create_table_options()).classes("target")

        lable_server_data = server_data_checker.create_elements(table)

        ui.button(
            "set data",
            on_click=lambda: (
                table.set_data([{"id": 1, "name": "bar-set-data", "age": "12"}]),
                lable_server_data.set_text(str(table.data)),
            ),
        )

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    # set data
    page.get_by_role("button").filter(has_text="set data").click()
    check_table_rows(table_locator, [["bar-set-data", "12"]])

    server_data_checker.expect_server_data(page)


def test_replace_data(browser: BrowserManager, page_path: str):
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(create_table_options()).classes("target")

        label_server_data = server_data_checker.create_elements(table)

        ui.button(
            "replace data",
            on_click=lambda: (
                table.replace_data(
                    [{"id": 1, "name": "bar-replace-data", "age": "12"}]
                ),
                label_server_data.set_text(str(table.data)),
            ),
        )

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    # set data
    page.get_by_role("button").filter(has_text="replace data").click()
    check_table_rows(table_locator, [["bar-replace-data", "12"]])

    server_data_checker.expect_server_data(page)


def test_update_data(browser: BrowserManager, page_path: str):
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(create_table_options()).classes("target")

        label_server_data = server_data_checker.create_elements(table)

        ui.button(
            "update data",
            on_click=lambda: (
                table.update_data([{"id": 1, "name": "bar-update-data", "age": "12"}]),
                label_server_data.set_text(str(table.data)),
            ),
        )

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    # set data
    page.get_by_role("button").filter(has_text="update data").click()
    check_table_rows(table_locator, [["bar-update-data", "12"], ["foo", "1"]])

    server_data_checker.expect_server_data(page)


def test_add_data(browser: BrowserManager, page_path: str):
    table_data = create_table_options()
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(table_data).classes("target")

        label_server_data = server_data_checker.create_elements(table)

        ui.button(
            "add data",
            on_click=lambda: (
                table.add_data([{"id": 3, "name": "bar-add-data", "age": "99"}]),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("add-data")

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    # add data
    page.locator(".add-data").click()
    check_table_rows(
        table_locator, [["bar", "12"], ["foo", "1"], ["bar-add-data", "99"]]
    )

    server_data_checker.expect_server_data(page)


def test_add_data_with_at_top(browser: BrowserManager, page_path: str):
    table_data = create_table_options()
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(table_data).classes("target")

        label_server_data = server_data_checker.create_elements(table)

        ui.button(
            "add data at top",
            on_click=lambda: (
                table.add_data(
                    [{"id": 3, "name": "new-bar1", "age": "99"}], at_top=True
                ),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("at-top")

        ui.button(
            "add data at bottom",
            on_click=lambda: (
                table.add_data(
                    [{"id": 4, "name": "new-bar2", "age": "99"}], at_top=False
                ),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("at-bottom")

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    # add data
    page.locator(".at-top").click()
    check_table_rows(table_locator, [["new-bar1", "99"], ["bar", "12"], ["foo", "1"]])

    server_data_checker.expect_server_data(page)

    # at bottom
    page.locator(".at-bottom").click()
    check_table_rows(
        table_locator,
        [
            ["new-bar1", "99"],
            ["bar", "12"],
            ["foo", "1"],
            ["new-bar2", "99"],
        ],
    )

    server_data_checker.expect_server_data(page)


def test_add_data_with_index(browser: BrowserManager, page_path: str):
    table_data = create_table_options()
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(table_data).classes("target")

        label_server_data = server_data_checker.create_elements(table)

        ui.button(
            "with index without at top",
            on_click=lambda: (
                table.add_data([{"id": 3, "name": "new-bar1", "age": "99"}], index=2),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("index-without-top")

        ui.button(
            "with index at top",
            on_click=lambda: (
                table.add_data(
                    [{"id": 4, "name": "new-bar2", "age": "99"}], at_top=False, index=2
                ),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("index-at-bottom")

        ui.button(
            "with index at top",
            on_click=lambda: (
                table.add_data(
                    [{"id": 5, "name": "new-bar3", "age": "99"}], at_top=True, index=2
                ),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("index-at-top")

        ui.button(
            "with index not exist at top",
            on_click=lambda: (
                table.add_data(
                    [{"id": 6, "name": "new-bar4", "age": "99"}], at_top=True, index=99
                ),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("index-not-exist-at-top")

        ui.button(
            "with index not exist at bottom",
            on_click=lambda: (
                table.add_data(
                    [{"id": 7, "name": "new-bar5", "age": "99"}], at_top=False, index=99
                ),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("index-not-exist-at-bottom")

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    # with index without at top
    page.locator(".index-without-top").click()
    check_table_rows(table_locator, [["bar", "12"], ["foo", "1"], ["new-bar1", "99"]])

    server_data_checker.expect_server_data(page)

    #  with index at buttom
    page.locator(".index-at-bottom").click()
    check_table_rows(
        table_locator,
        [
            ["bar", "12"],
            ["foo", "1"],
            ["new-bar2", "99"],
            ["new-bar1", "99"],
        ],
    )

    server_data_checker.expect_server_data(page)

    #  with index at top
    page.locator(".index-at-top").click()
    check_table_rows(
        table_locator,
        [
            ["bar", "12"],
            ["new-bar3", "99"],
            ["foo", "1"],
            ["new-bar2", "99"],
            ["new-bar1", "99"],
        ],
    )

    server_data_checker.expect_server_data(page)

    # with index not exist at top
    page.locator(".index-not-exist-at-top").click()
    check_table_rows(
        table_locator,
        [
            ["new-bar4", "99"],
            ["bar", "12"],
            ["new-bar3", "99"],
            ["foo", "1"],
            ["new-bar2", "99"],
            ["new-bar1", "99"],
        ],
    )

    server_data_checker.expect_server_data(page)

    # with index not exist at bottom
    page.locator(".index-not-exist-at-bottom").click()
    check_table_rows(
        table_locator,
        [
            ["new-bar4", "99"],
            ["bar", "12"],
            ["new-bar3", "99"],
            ["foo", "1"],
            ["new-bar2", "99"],
            ["new-bar1", "99"],
            ["new-bar5", "99"],
        ],
    )

    server_data_checker.expect_server_data(page)


def test_update_or_add_data(browser: BrowserManager, page_path: str):
    table_data = create_table_options()
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(table_data).classes("target")

        label_server_data = server_data_checker.create_elements(table)

        ui.button(
            "update_or_add_data",
            on_click=lambda: (
                table.update_or_add_data(
                    [
                        {"id": 3, "name": "bar-add-data", "age": "99"},
                        {"id": 2, "name": "bar-update-data", "age": "99"},
                    ]
                ),
                label_server_data.set_text(str(table.data)),
            ),
        ).classes("update-or-add-data")

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    page.locator(".update-or-add-data").click()
    check_table_rows(
        table_locator,
        [["bar", "12"], ["bar-update-data", "99"], ["bar-add-data", "99"]],
    )

    server_data_checker.expect_server_data(page)


def test_clear_data(browser: BrowserManager, page_path: str):
    server_data_checker = ServerDataChecker()

    @ui.page(page_path)
    def _():
        table = tabulator(create_table_options()).classes("target")

        label_server_data = server_data_checker.create_elements(table)

        ui.button(
            "clear data",
            on_click=lambda: (
                table.clear_data(),
                label_server_data.set_text(str(table.data)),
            ),
        )

    page = browser.open(page_path)
    table_locator = page.locator(".target")

    page.get_by_role("button").filter(has_text=re.compile("^clear data$")).click()
    check_table_rows(
        table_locator,
        [],
    )

    server_data_checker.expect_server_data(page)


def test_table_creation_and_method_call_after_page_load(
    browser: BrowserManager, page_path: str
):
    @ui.page(page_path)
    def _():
        df = pd.DataFrame({"index": [1, 2]})

        def build_table():
            table = tabulator.from_pandas(df).style("font-size: 75%")
            table.update_column_definition("index", {"title": "works"})

        ui.button("build table", on_click=build_table).props("no-caps")

    page = browser.open(page_path)

    page.get_by_text("build table").click()

    body_expect = expect(page.locator("body"))
    body_expect.to_contain_text("works")
