import unittest
from datetime import date, datetime, timedelta
from unittest import mock
from uuid import uuid4

import factory
from faker import Faker
from mock import MagicMock
from requests import Response

from ynab.api import (
    MAX_COMPARE_DAYS,
    YNAB,
    ImportIdGenerator,
    Transaction,
    TransactionStore,
    pretty_format_transactions,
    transactions_difference,
)
from ynab.secrets import Keyring

faker = Faker()


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
            transaction_date=date(year=2018, month=4, day=13),
            payee_name="a very long payee name that will be longer than 50 characters",
            memo=(
                "do not forget to say a very long string that should go over the "
                "limit of the number of characters you are allowed to enter in"
            ),
            amount=12.3456,
        )
        store.append(
            transaction_date=date(year=2018, month=4, day=13),
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
        self.assertEqual(expected, store.json("some-account-id"))

    def test_get(self):
        account_id = str(uuid4())

        for payee_name, memo in [(faker.name(), faker.sentence()), (None, None)]:
            ynab_response = {
                "data": {
                    "transactions": [
                        {
                            "id": str(uuid4()),
                            "date": "2019-11-16",
                            "amount": -9500,
                            "memo": memo,
                            "cleared": "reconciled",
                            "approved": True,
                            "flag_color": None,
                            "account_id": account_id,
                            "account_name": faker.word(),
                            "payee_id": None,
                            "payee_name": payee_name,
                            "category_id": str(uuid4()),
                            "category_name": faker.word(),
                            "transfer_account_id": None,
                            "transfer_transaction_id": None,
                            "matched_transaction_id": None,
                            "import_id": "YNAB:-9500:2019-11-16:1",
                            "deleted": False,
                            "subtransactions": [],
                        },
                        # deleted transaction
                        {
                            "date": "2019-11-16",
                            "amount": -9501,
                            "memo": memo,
                            "payee_name": payee_name,
                            "import_id": "YNAB:-9501:2019-11-16:1",
                            "deleted": True,
                        },
                    ]
                }
            }

            mock_response = MagicMock(spec=Response)
            mock_response.json.return_value = ynab_response
            mock_keyring = MagicMock(spec=Keyring)
            with mock.patch.object(YNAB, "secret", return_value="some_secret"):
                with mock.patch.object(YNAB, "validate_secrets", return_value=True):
                    ynab = YNAB.from_config(
                        {"secrets_keys": {"access_token": ""}}, keyring=mock_keyring
                    )

                    with mock.patch("requests.get", return_value=mock_response):
                        transactions = ynab.get("account_id", "budget_id")
                        self.assertEqual(
                            transactions.count(), 1
                        )  # no deleted transaction
                        (t,) = transactions.transactions
                        self.assertEqual(t.date, date(2019, 11, 16))
                        self.assertEqual(t.payee_name, payee_name or "")
                        self.assertEqual(t.memo, memo or "")
                        self.assertEqual(t.milliunit_amount, -9500)


class TransactionFactory(factory.Factory):
    class Meta:
        model = Transaction

    date = factory.Faker("date_object")
    payee_name = factory.Faker("name")
    memo = factory.Faker("sentence")
    milliunit_amount = factory.Faker("pyint", min_value=1000)
    import_id = factory.LazyAttribute(
        lambda o: ImportIdGenerator().generate(o.date, o.milliunit_amount)
    )  # note: if two transactions are created on the same date they will have incorrect import ids


class TestTransactionsDifference(unittest.TestCase):
    no_difference = ([], [])

    def test_amount_equal_various_date_offsets(self):
        a = TransactionFactory()

        def b(offset):
            return TransactionFactory(
                date=a.date + timedelta(days=offset),
                milliunit_amount=a.milliunit_amount,
            )

        # if the offset is less than two days there is no difference
        self.assert_diff([a], [b(-1)], expected=self.no_difference)
        self.assert_diff([a], [b(+2)], expected=self.no_difference)

        # if the offset is greater than MAX_COMPARE_DAYS days then the two lists have
        # nothing in common
        b_ = b(-MAX_COMPARE_DAYS - 1)
        self.assert_diff([a], [b_], expected=([a], [b_]))

    def test_duplicates_respected(self):
        t = TransactionFactory()
        self.assert_diff([t, t], [t, t, t], expected=([], [t]))

    def test_empty_lists(self):
        self.assert_diff([], [], expected=self.no_difference)

    def test_best_match_on_memo(self):
        t = TransactionFactory(memo="This is a sentence", milliunit_amount=1000)
        t_different = TransactionFactory(
            memo="Something completely different", milliunit_amount=1000, date=t.date,
        )
        t_similar = TransactionFactory(
            memo="This is almost a sentence", milliunit_amount=1000, date=t.date,
        )

        expected = ([], [t_different])
        with self.subTest(msg="Different first"):
            self.assert_diff([t], [t_different, t_similar], expected)

        with self.subTest(msg="Similar first"):
            self.assert_diff([t], [t_similar, t_different], expected)

    def assert_diff(self, transactions_a, transactions_b, expected):
        diff = transactions_difference(transactions_a, transactions_b)
        self.assertEqual(diff, expected)


class TestPrettyFormatTransactions(unittest.TestCase):
    def test(self):
        string = pretty_format_transactions(
            [
                TransactionFactory(
                    date=date(1974, 7, 18),
                    payee_name="Hubert Blaine Wolfeschlegelsteinhausenbergerdorff",
                    milliunit_amount=-1256,
                    memo="Happy families are all alike; every unhappy family is unhappy in its own way",
                )
            ]
        )
        self.assertEqual(
            string,
            (
                "Date       Payee                Memo                                         Amount \n"
                "1974-07-18 Hubert Blaine Wo...  Happy families are all alike; every ...       -1.26\n"
            ),
        )
