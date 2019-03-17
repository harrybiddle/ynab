# -*- coding: utf-8 -*-

from ynab import fileutils
from ynab.bank import Bank


class DKB(Bank):
    full_name = "DKB"

    def __init__(self, config, secrets):
        super(DKB, self).__init__(secrets)
        self.validate_secrets("anmeldename", "pin")

    def download_transactions(self, driver, dir):
        self._login(driver)
        self._navigate_to_transactions(driver)
        self._download_transactions(driver)
        return fileutils.wait_for_file(dir, ".csv")

    def _login(self, driver):
        driver.get("https://www.dkb.de/banking")

        login = driver.find_element_by_id("loginInputSelector")
        login.send_keys(self.secret("anmeldename"))

        pin = driver.find_element_by_id("pinInputSelector")
        pin.send_keys(self.secret("pin"))

        button = driver.find_element_by_id("buttonlogin")
        button.click()

    def _navigate_to_transactions(self, driver):
        transactions = driver.find_element_by_xpath('//*[@id="menu_0.0.0-node"]/a')
        transactions.click()
        # In the current view you can select an account and date range: we
        # leave it as the default account and the default time range of 'the
        # last 30 days'

    def _download_transactions(self, driver):
        button = driver.find_element_by_xpath('//span[@title="CSV-Export"]')
        button.click()
