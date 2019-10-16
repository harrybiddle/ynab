# -*- coding: utf-8 -*-
import sys
from csv import DictReader
from datetime import datetime
from pprint import pformat

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    invisibility_of_element_located,
)
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from ynab import fileutils
from ynab.api import YNAB
from ynab.bank import Bank

NUMBER_LINES_TO_IGNORE_IN_CSV = 6  # DKB CSV file is preceeded by a 6-line header
DATE_FORMAT_IN_CSV = "%d.%m.%Y"
DKB_ENCODING = "iso-8859-1"
DKB_CSV_DELIMITER = ";"
DKB_2FA_TIMEOUT_SECONDS = 60

ACCOUNT_DATE_HEADER_NAME = "Buchungstag"
ACCOUNT_MEMO_HEADER_NAME = "Verwendungszweck"
AMOUNT_HEADER_NAME = "Betrag (EUR)"
CREDIT_CARD_MEMO_HEADER_NAME = "Beschreibung"
CREDIT_DATE_HEADER_NAME = "Belegdatum"
PAYEE_HEADER_NAME = "Auftraggeber"


class DKB(Bank):
    full_name = "DKB"

    def __init__(self, config, secrets):
        super(DKB, self).__init__(secrets)
        self.validate_secrets("anmeldename", "pin")
        self.account_substring = str(config["account_substring"])

    def fetch_transactions(self, driver, ynab: YNAB, dir: str):
        self._login(driver)
        self._wait_for_2fa(driver)
        self._navigate_to_transactions(driver)
        self._switch_to_correct_account(driver)
        self._download_transactions(driver)
        csv, = fileutils.wait_for_file(dir, ".csv")
        _add_transactions_from_csv(csv, ynab)

    def _login(self, driver):
        driver.get("https://www.dkb.de/banking")

        login = driver.find_element_by_id("loginInputSelector")
        login.send_keys(self.secret("anmeldename"))

        pin = driver.find_element_by_id("pinInputSelector")
        pin.send_keys(self.secret("pin"))

        button = driver.find_element_by_id("buttonlogin")
        button.click()

    def _wait_for_2fa(self, driver):
        # wait until we are on the 2fa page
        xpath_of_some_2fa_page_element = (
            "//*[text()[contains(.,'Anmeldung bestätigen')]]"
        )
        driver.find_element_by_xpath(xpath_of_some_2fa_page_element)

        # wait until we are off the 2fa page
        print(f"Waiting {DKB_2FA_TIMEOUT_SECONDS} seconds for 2FA...")
        WebDriverWait(driver, DKB_2FA_TIMEOUT_SECONDS).until(
            invisibility_of_element_located((By.XPATH, xpath_of_some_2fa_page_element))
        )
        print("Looks like 2FA passed")

    def _navigate_to_transactions(self, driver):
        transactions = driver.find_element_by_xpath('//*[@id="menu_0.0.0-node"]/a')
        transactions.click()
        # In the current view you can select an account and date range: we
        # leave it as the default account and the default time range of 'the
        # last 30 days'

    def _switch_to_correct_account(self, driver):
        all_accounts = Select(driver.find_element_by_name("slAllAccounts"))

        all_texts = [option.text for option in all_accounts.options]
        try:
            text, = [v for v in all_texts if self.account_substring in v]
        except ValueError as e:
            raise ValueError("Account substring does not match or is not unique") from e
        all_accounts.select_by_visible_text(text)

        update_button = driver.find_element_by_id("searchbutton")
        update_button.click()

    def _download_transactions(self, driver):
        button = driver.find_element_by_xpath('//span[@title="CSV-Export"]')
        button.click()


def _add_transactions_from_csv(filepath: str, ynab: YNAB):
    """
    Iterate over the entries in a CSV file from DKB and add them as transactions on the
    supplied YNAB object. Any entries with a date in the future are skipped.
    """

    def parse_german_float(string: str) -> float:
        """
        Parse a number like 12.002,34
        """
        string = string.replace(",", ".")
        string = string.replace(".", "", string.count(".") - 1)
        return float(string)

    with open(filepath, encoding=DKB_ENCODING) as file:
        # detect whether an account or a credit card: they are slightly different CSVs
        first_line = file.readline()
        if "Kreditkarte" in first_line:
            has_payee = False
            memo_header_name = CREDIT_CARD_MEMO_HEADER_NAME
            date_header_name = CREDIT_DATE_HEADER_NAME
        elif "Kontonummer" in first_line:
            has_payee = True
            memo_header_name = ACCOUNT_MEMO_HEADER_NAME
            date_header_name = ACCOUNT_DATE_HEADER_NAME
        else:
            raise ValueError(
                "Expected 'Kreditkarte' or 'Kontonummer' to be in the first line but "
                f"got {first_line}"
            )

        # skip the other NUMBER_LINES_TO_IGNORE_IN_CSV lines
        for _ in range(NUMBER_LINES_TO_IGNORE_IN_CSV - 1):
            file.readline()

        # read the rest as CSV
        reader = DictReader(file, delimiter=DKB_CSV_DELIMITER)
        if has_payee:
            payee_header, = [h for h in reader.fieldnames if PAYEE_HEADER_NAME in h]

        # insert into ynab object
        for row in reader:
            payee_name = row[payee_header] if has_payee else ""
            float_amount = parse_german_float(row[AMOUNT_HEADER_NAME])
            date = datetime.strptime(row[date_header_name], DATE_FORMAT_IN_CSV)
            memo = row[memo_header_name]
            if date > datetime.now():
                sys.stderr.write(
                    f"Skipping because it is in the future: \n{pformat(row)}\n"
                )
                continue

            ynab.add_transaction(
                date=date, payee_name=payee_name, memo=memo, amount=float_amount
            )
