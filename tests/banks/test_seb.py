import unittest
from datetime import date

from mock import MagicMock, call

from importlib_resources import path
from tests.banks import data
from ynab.api import TransactionStore
from ynab.banks.seb_se import _add_transactions_from_xlsx


class TestAddTransactionsFromXlsx(unittest.TestCase):
    def test_add(self):
        transaction_store = MagicMock(spec=TransactionStore)

        with path(data, "seb_example.xlsx") as p:
            _add_transactions_from_xlsx(p, transaction_store)

        self.assertEqual(
            transaction_store.append.call_args_list,
            [
                call(
                    amount=200,
                    transaction_date=date(2020, 1, 10),
                    memo="46724536420",
                    payee_name="",
                ),
                call(
                    amount=-37,
                    transaction_date=date(2020, 1, 24),
                    memo="AB STORSTOCK",
                    payee_name="",
                ),
                call(
                    amount=-100,
                    transaction_date=date(2020, 1, 26),
                    memo="46703634940",
                    payee_name="",
                ),
            ],
        )
