import unittest
from datetime import datetime
from importlib.resources import path

from mock import MagicMock, call

from tests.banks import data
from ynab.api import YNAB
from ynab.banks.dkb_de import _add_transactions_from_csv


class Any:
    def __eq__(self, other):
        return True


class TestAddTransactionsFromCSV(unittest.TestCase):
    def test_add_from_bank_example_file(self):
        ynab = MagicMock(spec=YNAB)

        with path(data, "dkb_bank_example.csv") as p:
            _add_transactions_from_csv(p, ynab)

        self.assertEqual(
            ynab.add_transaction.call_args_list,
            [
                call(
                    amount=-28.2,
                    date=datetime(2019, 5, 6, 0, 0),
                    memo=Any(),
                    payee_name="EC-POS EMV  0",
                ),
                call(
                    amount=-950.0,
                    date=datetime(2019, 5, 2, 0, 0),
                    memo="Auftrag",
                    payee_name="HOLGER POTTS",
                ),
            ],
        )

    def test_add_from_credit_card_example_file(self):
        ynab = MagicMock(spec=YNAB)

        with path(data, "dkb_credit_card_example.csv") as p:
            _add_transactions_from_csv(p, ynab)

        self.assertEqual(
            ynab.add_transaction.call_args_list,
            [
                call(
                    amount=-45.0,
                    date=datetime(2019, 5, 3, 0, 0),
                    memo="REISEBANK FRANKFURT ATM",
                    payee_name="",
                ),
                call(
                    amount=-1.0,
                    date=datetime(2019, 5, 3, 0, 0),
                    memo="THE SHOP LONDON",
                    payee_name="",
                ),
            ],
        )
