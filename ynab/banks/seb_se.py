from datetime import datetime

import xlrd
from ynab.api import TransactionStore


class ExcelFile:
    NUMBER_HEADER_ROWS = 8
    DATE_FORMAT = "%Y-%m-%d"
    DATE_COLUMN = 1  # "Value Date"
    MEMO_COLUMN = 3  # "Text"
    AMOUNT_COLUMN = 4  # "Amount"


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
