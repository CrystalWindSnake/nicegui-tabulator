from pathlib import Path
from typing import Literal, Optional
from nicegui import ui, app, Client

_ASSETS_DIR = Path(__file__).parent / "libs"

_T_THEME_NAME = Literal[
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
]

_remove_old_theme_js = """
    const linkElements = document.querySelectorAll('link.nicegui-tabulator-theme');
    linkElements.forEach(linkElement => {
        linkElement.parentNode.removeChild(linkElement);
    });
"""


def use_theme(theme_name: _T_THEME_NAME, shared: Optional[bool] = None) -> None:
    """Use a tabulator theme.

    Args:
        theme_name (_T_THEME_NAME):  name of the theme to use.
        shared (bool | None, optional):  Whether to use the theme for all clients or only the current client.
            `None`(default): use the theme for all clients if there is no client context (e.g. at startup), otherwise use it only for the current client.
            `True`: use the theme for all clients.
            `False`: use the theme only for the current client.

    ## Example

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
    """
    has_context = bool(ui.context.slot_stack)

    if shared is None:
        shared = not has_context

    css_name = (
        "tabulator.min.css"
        if theme_name == "default"
        else f"tabulator_{theme_name}.min.css"
    )
    css_path = _ASSETS_DIR / css_name

    if not css_path.exists():
        raise ValueError(f"theme '{css_path.resolve()}' not found")

    app.add_static_file(local_file=css_path, url_path="/" + css_name)

    clients_to_update = []
    if shared:
        clients_to_update.extend(list(Client.instances.values()))
    elif has_context:
        clients_to_update.append(ui.context.client)

    for client in clients_to_update:
        if client.has_socket_connection:
            client.run_javascript(_remove_old_theme_js)

    ui.add_head_html(
        rf'<link class="nicegui-tabulator-theme" rel="stylesheet" href="/{css_name}">',
        shared=shared,
    )
