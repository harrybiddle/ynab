from datetime import datetime

import xlrd
from ynab import fileutils
from ynab.api import TransactionStore
from ynab.bank import Bank


class ExcelFile:
    NUMBER_HEADER_ROWS = 8
    DATE_FORMAT = "%Y-%m-%d"
    DATE_COLUMN = 1  # "Value Date"
    MEMO_COLUMN = 3  # "Text"
    AMOUNT_COLUMN = 4  # "Amount"


class SEB(Bank):

    full_name = "SEB"

    def __init__(self, config, secrets):
        super().__init__(secrets)
        self.validate_secrets("personnummber", "pin")
        self.account_substring = str(config["account_substring"])

    def fetch_transactions(self, driver, transaction_store: TransactionStore, dir: str):
        self._login(driver)
        (csv,) = fileutils.wait_for_file(dir, ".xlsx")
        _add_transactions_from_xlsx(csv, transaction_store)

    def _login(self, driver):
        driver.get("https://www.seb.se/banking")

        login = driver.find_element_by_id("loginInputSelector")
        login.send_keys(self.secret("anmeldename"))

        pin = driver.find_element_by_id("pinInputSelector")
        pin.send_keys(self.secret("pin"))

        button = driver.find_element_by_id("buttonlogin")
        button.click()


def _add_transactions_from_xlsx(filepath: str, transaction_store: TransactionStore):
    """
    Iterate over the entries in a XLSX file from SEB and add them as transactions on the
    supplied YNAB object. The date is taken from the "value date". Any entries with a
    date in the future are skipped.
    """
    workbook = xlrd.open_workbook(filepath)
    worksheet = workbook.sheet_by_index(0)

    # iterate in reverse (the older transactions are at the bottom)
    for row in range(worksheet.nrows - 1, ExcelFile.NUMBER_HEADER_ROWS - 1, -1):
        # read values as strings
        date_string = worksheet.cell_value(row, ExcelFile.DATE_COLUMN)
        memo = worksheet.cell_value(row, ExcelFile.MEMO_COLUMN)
        amount_string = worksheet.cell_value(row, ExcelFile.AMOUNT_COLUMN)

        # parse strings
        transaction_date = datetime.strptime(date_string, ExcelFile.DATE_FORMAT).date()
        amount = float(amount_string)

        # insert transaction
        transaction_store.append(
            transaction_date=transaction_date, memo=memo, amount=amount, payee_name=""
        )
