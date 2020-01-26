import unittest
from datetime import date

from mock import MagicMock, call

from importlib_resources import path
from tests.banks import data
from ynab.api import TransactionStore
from ynab.banks.dkb_de import _add_transactions_from_csv


class Any:
    def __eq__(self, other):
        return True


class TestAddTransactionsFromCSV(unittest.TestCase):
    def test_add_from_bank_example_file(self):
        transaction_store = MagicMock(spec=TransactionStore)

        with path(data, "dkb_bank_example.csv") as p:
            _add_transactions_from_csv(p, transaction_store)

        self.assertEqual(
            transaction_store.append.call_args_list,
            [
                call(
                    amount=-28.2,
                    transaction_date=date(2019, 5, 6),
                    memo=Any(),
                    payee_name="EC-POS EMV  0",
                ),
                call(
                    amount=-950.0,
                    transaction_date=date(2019, 5, 2),
                    memo="Auftrag",
                    payee_name="HOLGER POTTS",
                ),
            ],
        )

    def test_add_from_credit_card_example_file(self):
        transaction_store = MagicMock(spec=TransactionStore)

        with path(data, "dkb_credit_card_example.csv") as p:
            _add_transactions_from_csv(p, transaction_store)

        self.assertEqual(
            transaction_store.append.call_args_list,
            [
                call(
                    amount=-45.0,
                    transaction_date=date(2019, 5, 3),
                    memo="REISEBANK FRANKFURT ATM",
                    payee_name="",
                ),
                call(
                    amount=-1.0,
                    transaction_date=date(2019, 5, 3),
                    memo="THE SHOP LONDON",
                    payee_name="",
                ),
            ],
        )
