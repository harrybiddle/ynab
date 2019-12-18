import selenium.webdriver

from ynab import fileutils
from ynab.bank import Bank


class Amex(Bank):
    full_name = "American Express"

    def __init__(self, config, secrets):
        super().__init__(secrets)
        self.validate_secrets("password")
        self.username = config["username"]

    def download_transactions(self, driver, dir):
        self._start_download(driver)
        return self._wait_until_download_complete(dir)

    def _start_download(self, driver):
        self._go_to_website(driver)
        self._log_in(driver)
        self._navigate_to_downloads_page(driver)
        self._initiate_download(driver)

    def _wait_until_download_complete(self, dir):
        return fileutils.wait_for_file(dir, ".qfx")[0]

    def _go_to_website(self, driver):
        driver.get("https://www.americanexpress.com/uk/")
        assert "American Express" in driver.title

        # bypass cookie question
        driver.find_element_by_id("sprite-ContinueButton_EN").click()

    def _log_in(self, driver):
        user_id = driver.find_element_by_name("UserID")
        user_id.send_keys(self.username)

        password = driver.find_element_by_id("Password")
        password.send_keys(self.secret("password"))

        # click through to log in
        loginButton = driver.find_element_by_id("loginButton")
        loginButton.click()

    def _navigate_to_downloads_page(self, driver):
        tab = driver.find_element_by_id("gb_myca_pc_statement")
        export = driver.find_element_by_id(
            ("gb_myca_pc_statement_export_" "statement_data")
        )

        action = selenium.webdriver.ActionChains(driver)
        action.move_to_element(tab)
        action.click(export)
        action.perform()

    def _initiate_download(self, driver):
        driver.find_element_by_id("quicken").click()

        driver.find_element_by_id("select0").click()

        # get the latest two statements
        driver.find_element_by_id("checkboxid00").click()
        driver.find_element_by_id("checkboxid01").click()

        # kick off the download
        driver.find_element_by_id("myBlueButton1").click()
