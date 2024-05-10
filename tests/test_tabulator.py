from nicegui import ui
from .screen import BrowserManager
from playwright.sync_api import expect, Locator
from nicegui_tabulator import tabulator


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
    page.wait_for_timeout(1000)

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
