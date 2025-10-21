from typing import Final, Optional
from nicegui import ui

LUXON_DEFAULT_SCRIPT_URL: Final[str] = "https://cdn.jsdelivr.net/npm/luxon@3/build/global/luxon.min.js"


def import_luxon(shared: Optional[bool] = None, script_url: str = LUXON_DEFAULT_SCRIPT_URL):
    """Inject Luxon into the page so Tabulator date/time features can work.

       Tabulator's date/time formatters and sorters require Luxon to be available in the
       browser environment. Call this function **before** creating tables that use any of:
       - ``formatter: "datetime"``
       - ``sorter: "date"`` or ``sorter: "datetime"``
       - editors that depend on Luxon (if used in the future)

       Args:
           shared:  Whether to import the dependency for all clients or only the current client.
            `None`(default): import the dependency for all clients if the current client is an auto-index client, otherwise use it only for the current client.
            `True`: import for all clients.
            `False`: import only for the current client.
           script_url: The URL of Luxon's global build. Override this if you self-host
               Luxon or want to pin to a different version.

       Notes:
           - Call it once during your page/app setup, before creating Tabulator grids that
             require date/time formatting/sorting.
       """
    if shared is None:
        shared = ui.context.client.is_auto_index_client

    ui.add_head_html(f'<script src="{script_url}"></script>', shared=shared)
