import threading
import os
from playwright.sync_api import Browser
from nicegui import ui, app
from nicegui.testing.general_fixtures import prepare_simulation
from nicegui.server import Server

PORT = 3392
os.environ["NICEGUI_SCREEN_TEST_PORT"] = str(PORT)


class ServerManager:
    def __init__(self, browser: Browser) -> None:
        self.server_thread = None
        self.browser = browser

        self._context = browser.new_context()
        self._context.set_default_timeout(10000)

        self.ui_run_kwargs = {
            "port": PORT,
            "show": False,
            "reload": False,
        }
        self.connected = threading.Event()

        app.on_startup(self.connected.set)

    def start_server(self) -> None:
        """Start the webserver in a separate thread. This is the equivalent of `ui.run()` in a normal script."""
        prepare_simulation()
        self.server_thread = threading.Thread(
            target=lambda: ui.run(**self.ui_run_kwargs)
        )
        self.server_thread.start()

    def stop_server(self) -> None:
        """Stop the webserver."""
        self.browser.close()
        Server.instance.should_exit = True

        if self.server_thread:
            self.server_thread.join()

    def new_page(self):
        if self.server_thread is None:
            self.start_server()

        # self.connected.clear()
        is_connected = self.connected.wait(5)
        if not is_connected:
            raise TimeoutError("Failed to connect to server")
        return BrowserManager(self)


class BrowserManager:
    def __init__(self, server: ServerManager) -> None:
        self.__server = server
        self._page = self.__server._context.new_page()

    def open(self, path: str):
        # wait for server to be ready

        self._page.goto(
            f"http://localhost:{PORT}{path}",
            timeout=5000,
            wait_until="domcontentloaded",
        )

        self._page.wait_for_timeout(600)
        return self._page

    def close(self):
        self._page.close()

    @property
    def pw_page(self):
        return self._page
