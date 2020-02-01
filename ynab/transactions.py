from collections import namedtuple
from textwrap import shorten
from typing import Iterable

import fuzzywuzzy.process

Transaction = namedtuple(
    "Transaction", ["date", "payee_name", "memo", "milliunit_amount", "import_id"]
)


class CompareTransactions:
    def __init__(self, transaction):
        self.transaction = transaction

    def __eq__(self, other):
        milliunit_difference = abs(
            self.transaction.milliunit_amount - other.transaction.milliunit_amount
        )
        days_difference = abs(self.transaction.date - other.transaction.date).days
        return (
            milliunit_difference < 2  # ignore very minor differences in milliunits
            and days_difference <= MAX_COMPARE_DAYS
        )


def transactions_difference(
    transactions_a: Iterable[Transaction], transactions_b: Iterable[Transaction]
):
    def subtract(transactions_c, transactions_d):
        remaining = transactions_c.copy()
        for transaction in transactions_d:
            comparable = CompareTransactions(transaction)
            comparables = [CompareTransactions(t) for t in remaining]
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
    def truncate(width, obj, right=False):
        stringified = str(obj or "")
        truncated = shorten(stringified, width=width, placeholder="...")
        return truncated.rjust(width) if right else truncated.ljust(width)

    widths = [10, 20, 40, 10]

    # header line
    header_columns = [
        truncate(widths[0], "Date"),
        truncate(widths[1], "Payee"),
        truncate(widths[2], "Memo"),
        truncate(widths[3], "Amount", right=True),
    ]
    header_line = " ".join(header_columns)

    # data lines
    lines = [header_line]
    for transaction in transactions:
        amount_str = f"{transaction.milliunit_amount / 1000:.2f}"
        columns = [
            truncate(widths[0], transaction.date),
            truncate(widths[1], transaction.payee_name),
            truncate(widths[2], transaction.memo),
            truncate(widths[3], amount_str, right=True),
        ]
        line = " ".join(columns)
        lines.append(line)

    return "\n".join(lines)


MAX_COMPARE_DAYS = 7
