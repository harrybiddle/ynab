import unittest
from datetime import date, timedelta

import factory

from ynab.api import ImportIdGenerator
from ynab.transactions import (
    MAX_COMPARE_DAYS,
    Transaction,
    pretty_format_transactions,
    transactions_difference,
)


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
        transactions = [
            Transaction(
                date=date(2017, 5, 2),
                payee_name="Mr Tibbles",
                memo="Goes to market",
                milliunit_amount=123456789,
                import_id="foo",
            ),
            Transaction(
                date=date(2011, 1, 1),
                payee_name="This is a really very long payee name",
                memo="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed d",
                milliunit_amount=-962,
                import_id="bar",
            ),
            Transaction(
                date=date(2012, 1, 1),
                payee_name=None,
                memo=None,
                milliunit_amount=-962,
                import_id="bar",
            ),
        ]
        string = pretty_format_transactions(transactions)
        print(string)
        self.assertEqual(
            string.split("\n"),
            [
                "Date       Payee                Memo                                         Amount",
                "2017-05-02 Mr Tibbles           Goes to market                            123456.79",
                "2011-01-01 This is a really...  Lorem ipsum dolor sit amet,...                -0.96",
                "2012-01-01                                                                    -0.96",
            ],
        )
