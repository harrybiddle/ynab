"""
Module for interacting with YouNeedABudget's API
"""

from collections import Counter
from datetime import datetime
from types import SimpleNamespace

import requests
from requests import Response

from .bank import ObjectWithSecrets

DATE_FORMAT_FOR_YNAB = "%Y-%m-%d"
CHARACTER_LIMIT_FOR_PAYEE_NAME = 50
CHARACTER_LIMIT_FOR_MEMO = 100


class ImportIdGenerator:
    def __init__(self):
        self.counter = Counter()

    def generate(self, date: datetime, milliunit_amount: int) -> str:
        iso_date = date.strftime(DATE_FORMAT_FOR_YNAB)
        id_without_occurence = (
            f"YNAB:{milliunit_amount}:{iso_date}"
        )  # e.g. "YNAB:-294230:2015-12-30"

        self.counter.update([id_without_occurence])
        occurrence = self.counter[id_without_occurence]
        assert occurrence > 0

        return (
            f"{id_without_occurence}:{occurrence}"
        )  # e.g. "YNAB:-294230:2015-12-30:1"


class TransactionStore:
    """
    Transactions to be uploaded to YNAB.
    """

    def __init__(self):
        self.import_id_generator = ImportIdGenerator()
        self.transactions = []

    def append(
        self, account_id: str, date: datetime, payee_name: str, memo: str, amount: float
    ):
        """
        Parses an entry to be appropriate to send to YNAB and inserts in into an
        internal list

        :raises ValueError: if the date is in the future
        """
        milliunit_amount = int(round(amount, 3) * 1000)
        transaction = SimpleNamespace(
            account_id=account_id,
            date=date.strftime(DATE_FORMAT_FOR_YNAB),
            payee_name=payee_name[:CHARACTER_LIMIT_FOR_PAYEE_NAME],
            memo=memo[-CHARACTER_LIMIT_FOR_MEMO:],
            milliunit_amount=milliunit_amount,
            import_id=self.import_id_generator.generate(date, milliunit_amount),
        )
        if date > datetime.now():
            raise ValueError(
                f"The date {date} is in the future and will be rejected by YNAB"
            )
        self.transactions.append(transaction)

    @property
    def json(self):
        """
        All entries as a nested list/dictionary ready to be sent to the YNAB endpoint.
        """
        return {
            "transactions": [
                {
                    "account_id": t.account_id,
                    "date": t.date,
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

    def __len__(self):
        return len(self.transactions)


class YNAB(ObjectWithSecrets):
    def __init__(self, _, secrets):
        super().__init__(secrets)
        self.validate_secrets("access_token")
        self.transaction_store = TransactionStore()
        self.defaults = {}

    def add_transaction(self, **kwargs):
        for key, value in self.defaults.items():
            kwargs.setdefault(key, value)
        self.transaction_store.append(**kwargs)

    def set_default(self, key, value):
        self.defaults[key] = value

    def count(self):
        return len(self.transaction_store)

    def push(self, budget_id: str) -> Response:
        """
        Pushes all transactions to YNAB. After pushing all previously-added transactions
        are cleared.

        :raises HTTPError: if one occurred
        :return: response from the YNAB API
        """
        url = f"https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions/bulk"
        access_token = self.secret("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, json=self.transaction_store.json, headers=headers)
        response.raise_for_status()
        self.transaction_store.clear()
        return response
