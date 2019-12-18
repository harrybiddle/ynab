"""
Module for interacting with YouNeedABudget's API
"""
from collections import Counter, namedtuple
from datetime import date, datetime, timedelta
from typing import Iterable

import fuzzywuzzy.process
import requests
from requests import Response

from ynab.bank import ObjectWithSecrets

DATE_FORMAT_FOR_YNAB = "%Y-%m-%d"
CHARACTER_LIMIT_FOR_PAYEE_NAME = 50
CHARACTER_LIMIT_FOR_MEMO = 100
MAX_COMPARE_DAYS = 7
BANK_DATE_RANGE = 30


class ImportIdGenerator:
    def __init__(self):
        self.counter = Counter()

    def generate(self, date: datetime, milliunit_amount: int) -> str:
        iso_date = date.strftime(DATE_FORMAT_FOR_YNAB)
        id_without_occurence = (
            f"YNAB:{milliunit_amount}:{iso_date}"  # e.g. "YNAB:-294230:2015-12-30"
        )

        self.counter.update([id_without_occurence])
        occurrence = self.counter[id_without_occurence]
        assert occurrence > 0

        return (
            f"{id_without_occurence}:{occurrence}"  # e.g. "YNAB:-294230:2015-12-30:1"
        )


Transaction = namedtuple(
    "Transaction", ["date", "payee_name", "memo", "milliunit_amount", "import_id"]
)


class TransactionStore:
    """
    Transactions to be uploaded to YNAB.
    """

    def __init__(self, transactions=None):
        self.import_id_generator = ImportIdGenerator()
        self.transactions = transactions or []

    def append(self, transaction_date: date, payee_name: str, memo: str, amount: float):
        """
        Parses an entry to be appropriate to send to YNAB and inserts in into an
        internal list

        :raises ValueError: if the date is in the future
        """
        transaction_date = date(
            transaction_date.year, transaction_date.month, transaction_date.day
        )
        milliunit_amount = int(round(amount, 3) * 1000)
        transaction = Transaction(
            date=transaction_date,
            payee_name=payee_name[:CHARACTER_LIMIT_FOR_PAYEE_NAME],
            memo=memo[-CHARACTER_LIMIT_FOR_MEMO:],
            milliunit_amount=milliunit_amount,
            import_id=self.import_id_generator.generate(
                transaction_date, milliunit_amount
            ),
        )
        if transaction_date > date.today():
            raise ValueError(
                f"The date {date} is in the future and will be rejected by YNAB"
            )
        self.transactions.append(transaction)

    def json(self, account_id: str):
        """
        All entries as a nested list/dictionary ready to be sent to the YNAB endpoint.
        """
        return {
            "transactions": [
                {
                    "account_id": account_id,
                    "date": t.date.strftime(DATE_FORMAT_FOR_YNAB),
                    "amount": t.milliunit_amount,
                    # "payee_id": None,
                    "payee_name": t.payee_name,
                    # "category_id": None,
                    "memo": t.memo,
                    "cleared": "cleared",
                    # "approved": False,
                    # "flag_color": "red",
                    "import_id": t.import_id,
                }
                for t in self.transactions
            ]
        }

    def clear(self):
        self.transactions = []

    def count(self):
        return len(self.transactions)


class YNAB(ObjectWithSecrets):
    def __init__(self, _, secrets):
        super().__init__(secrets)
        self.validate_secrets("access_token")

    def push(
        self, transaction_store: TransactionStore, account_id: str, budget_id: str
    ) -> Response:
        """
        Pushes all transactions to YNAB. After pushing all previously-added transactions
        are cleared.

        :raises HTTPError: if one occurred
        :return: response from the YNAB API
        """
        url = self._url(f"/budgets/{budget_id}/transactions/bulk")
        payload = transaction_store.json(account_id)
        response = requests.post(url, json=payload, headers=self._request_headers())
        response.raise_for_status()
        return response

    def get(self, account_id: str, budget_id: str) -> TransactionStore:
        transaction_store = TransactionStore()
        url = self._url(f"/budgets/{budget_id}/accounts/{account_id}/transactions")
        since_date = date.today() - timedelta(days=BANK_DATE_RANGE)
        response = requests.get(
            url,
            params={"since_date": since_date.strftime(DATE_FORMAT_FOR_YNAB)},
            headers=self._request_headers(),
        )
        response.raise_for_status()
        for transaction in response.json()["data"]["transactions"]:
            if not transaction["deleted"]:
                transaction_store.append(
                    transaction_date=datetime.strptime(
                        transaction["date"], DATE_FORMAT_FOR_YNAB
                    ),
                    payee_name=transaction["payee_name"] or "",
                    memo=transaction["memo"] or "",
                    amount=int(transaction["amount"]) / 1000,
                )
        return transaction_store

    @staticmethod
    def _url(endpoint):
        return "https://api.youneedabudget.com/v1/" + endpoint.lstrip("/")

    def _request_headers(self):
        access_token = self.secret("access_token")
        return {"Authorization": f"Bearer {access_token}"}


def transactions_difference(
    transactions_a: Iterable[Transaction], transactions_b: Iterable[Transaction]
):
    class Comparable:
        def __init__(self, transaction):
            self.transaction = transaction

        def __eq__(self, other):
            return (
                abs(
                    self.transaction.milliunit_amount
                    - other.transaction.milliunit_amount
                )
                < 2  # ignore very minor differences in milliunits
                and abs(self.transaction.date - other.transaction.date).days
                <= MAX_COMPARE_DAYS
            )

    def subtract(transactions_c, transactions_d):
        remaining = transactions_c.copy()
        for transaction in transactions_d:
            comparable = Comparable(transaction)
            comparables = [Comparable(t) for t in remaining]
            if comparable in comparables:
                candidates = [c for c in comparables if c == comparable]
                best_matching_memo, _ = fuzzywuzzy.process.extractOne(
                    query=transaction.memo,
                    choices=[c.transaction.memo for c in candidates],
                )
                best_match = next(
                    c for c in candidates if c.transaction.memo == best_matching_memo
                )
                remaining.remove(best_match.transaction)

        return remaining

    return (
        subtract(transactions_a, transactions_b),
        subtract(transactions_b, transactions_a),
    )


def pretty_format_transactions(transactions: Iterable[Transaction]):
    def justify(x, width, right=False):
        string = str(x)
        if len(string) > width:
            string = string[0 : width - 4] + "... "
        if right:
            return string.rjust(width)
        else:
            return string.ljust(width)

    header = ["Date", "Payee", "Memo", "    Amount"]
    widths = [10, 20, 40, 10]  # each width should be at least 5

    # print header
    ret = ""
    for text, width in zip(header, widths):
        ret += justify(text, width) + " "
    ret += "\n"

    # print data
    for transaction in transactions:
        ret += justify(transaction.date, widths[0]) + " "
        ret += justify(transaction.payee_name or "", widths[1]) + " "
        ret += justify(transaction.memo or "", widths[2]) + " "
        ret += justify(
            f"{transaction.milliunit_amount / 1000:.2f}", widths[3], right=True
        )
        ret += "\n"

    return ret
