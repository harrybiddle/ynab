import unittest
from datetime import datetime

from ynab.api import ImportIdGenerator, TransactionStore


class TestApi(unittest.TestCase):
    def test_import_id_generator(self):
        generator = ImportIdGenerator()
        ids = [
            generator.generate(
                date=datetime(year=2018, month=4, day=13, hour=3, minute=44),
                milliunit_amount=12345,
            ),
            generator.generate(
                date=datetime(year=2018, month=4, day=13, hour=3, minute=44),
                milliunit_amount=12345,
            ),
            generator.generate(
                date=datetime(year=2014, month=8, day=1, hour=16, minute=14),
                milliunit_amount=5432,
            ),
        ]
        expected = [
            "YNAB:12345:2018-04-13:1",
            "YNAB:12345:2018-04-13:2",
            "YNAB:5432:2014-08-01:1",
        ]
        self.assertEqual(ids, expected)

    def test_api(self):
        store = TransactionStore()
        store.append(
            account_id="some-account-id",
            date=datetime(year=2018, month=4, day=13, hour=3, minute=44),
            payee_name="a very long payee name that will be longer than 50 characters",
            memo=(
                "do not forget to say a very long string that should go over the "
                "limit of the number of characters you are allowed to enter in"
            ),
            amount=12.3456,
        )
        store.append(
            account_id="some-account-id",
            date=datetime(year=2018, month=4, day=13, hour=3, minute=44),
            payee_name="obama",
            memo="this memo is ok",
            amount=-120_000,
        )
        expected = {
            "transactions": [
                {
                    "account_id": "some-account-id",
                    "date": "2018-04-13",
                    "amount": 12346,
                    "payee_name": "a very long payee name that will be longer than 50",
                    "memo": (
                        "ry long string that should go over the limit of the number of "
                        "characters you are allowed to enter in"
                    ),
                    "import_id": "YNAB:12346:2018-04-13:1",
                    "cleared": "cleared",
                },
                {
                    "account_id": "some-account-id",
                    "date": "2018-04-13",
                    "amount": -120_000_000,
                    "payee_name": "obama",
                    "memo": "this memo is ok",
                    "import_id": "YNAB:-120000000:2018-04-13:1",
                    "cleared": "cleared",
                },
            ]
        }
        self.assertEqual(expected, store.json)
