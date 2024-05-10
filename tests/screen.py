import threading
from playwright.sync_api import Browser
from nicegui import ui
from nicegui.server import Server

PORT = 3392


class ServerManager:
    def __init__(self, browser: Browser) -> None:
        self.server_thread = None
        self.browser = browser

        self._context = browser.new_context()
        self._context.set_default_timeout(10000)
        self.ui_run_kwargs = {"port": PORT, "show": False, "reload": False}

    def start_server(self) -> None:
        """Start the webserver in a separate thread. This is the equivalent of `ui.run()` in a normal script."""
        self.server_thread = threading.Thread(target=ui.run, kwargs=self.ui_run_kwargs)
        self.server_thread.start()

    def stop_server(self) -> None:
        """Stop the webserver."""
        # self.close()
        # self.caplog.clear()
        self.browser.close()
        Server.instance.should_exit = True

        if self.server_thread:
            self.server_thread.join()

    def new_page(self):
        if self.server_thread is None:
            self.start_server()

        return BrowserManager(self)


class BrowserManager:
    def __init__(self, server: ServerManager) -> None:
        self.__server = server
        self._page = self.__server._context.new_page()
        # self._page.set_default_timeout(5000)

    def open(self, path: str):
        # self._page.wait_for_selector("body", timeout=10000)
        self._page.goto(f"http://localhost:{PORT}{path}", wait_until="domcontentloaded")
        return self._page

    def close(self):
        self._page.close()

    @property
    def pw_page(self):
        return self._page