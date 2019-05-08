import os
import tempfile
from datetime import datetime

from selenium import webdriver


class Chrome(webdriver.Chrome):
    """ An optionally headless Chrome with a preset download directory """

    @classmethod
    def construct(cls, download_directory: str, headless: bool):
        options = webdriver.chrome.options.Options()
        prefs = {"download.default_directory": download_directory}
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--window-size=1920x1080")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        driver = cls(chrome_options=options)
        driver._enable_download_in_headless_chrome(download_directory)
        driver.implicitly_wait(10)
        return driver

    def take_screenshot(self) -> str:
        """ Save a screenshot in a temporary directory and return its path """

        directory = tempfile.gettempdir()
        basename = datetime.now().strftime("%d-%b-%y-%H:%m:%S")
        filename = "{}.png".format(basename)
        path = os.path.join(directory, filename)
        self.get_screenshot_as_file(path)
        return path

    def _enable_download_in_headless_chrome(self, download_dir):
        """ Workaround for a bug in Chromium. See comment #86 of the below link:
        https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        """
        self.command_executor._commands["send_command"] = (
            "POST",
            "/session/$sessionId/chromium/send_command",
        )  # noqa
        params = {
            "cmd": "Page.setDownloadBehavior",
            "params": {"behavior": "allow", "downloadPath": download_dir},
        }
        self.execute("send_command", params)
