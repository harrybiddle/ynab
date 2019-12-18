#! /usr/bin/env python3
"""
Pull down and import transaction histories into ynab.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from collections import namedtuple
from datetime import date, timedelta
from pprint import pprint

from selenium.common.exceptions import TimeoutException, WebDriverException

from ynab import __version__, config_schema
from ynab.api import (  # norc
    BANK_DATE_RANGE,
    MAX_COMPARE_DAYS,
    YNAB,
    TransactionStore,
    pretty_format_transactions,
    transactions_difference,
)
from ynab.chrome import Chrome
from ynab.secrets import Keyring

TEMPORARY_DIRECTORY_PARENT = os.path.expanduser("~/Downloads")

Target = namedtuple("BankTarget", ["bank", "budget_id", "account_id"])


def _parse_arguments(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "configuration_file",
        type=str,
        default=os.path.expanduser("~/.ynab.conf"),
        nargs="?",
        help="defaults to ~/.ynab.conf",
    )
    parser.add_argument(
        "--headless", action="store_true", help="Do not open a visible browser window"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Do not delete downloaded transaction data",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    return parser.parse_args(args)


def _construct_target(config, keyring):
    bank_type = config.pop("type")
    class_ = config_schema.BANKS[bank_type]
    bank = class_.from_config(config, keyring)
    budget_id = config["target"]["budget_id"]
    account_id = config["target"]["account_id"]
    return Target(bank, budget_id, account_id)


def _fetch_transactions_from_bank(
    bank: Target, headless: bool, no_cleanup: bool, transaction_store: TransactionStore,
):
    download_directory = tempfile.mkdtemp(dir=TEMPORARY_DIRECTORY_PARENT)
    driver = Chrome.construct(download_directory, headless)

    try:
        bank.fetch_transactions(driver, transaction_store, download_directory)
    except (TimeoutException, WebDriverException) as e:
        sys.stderr.write(f"{e}\n")
        path = driver.take_screenshot()
        sys.stderr.write(f"Screenshot saved to {path}\n")
    finally:
        driver.quit()
        if no_cleanup:
            print(f"Leaving downloaded data in {download_directory}")
        else:
            print(f"Removing temporary directory {download_directory}")
            if os.path.exists(download_directory):
                shutil.rmtree(download_directory)


def main(argv=None):
    argv = argv or sys.argv[1:]
    args = _parse_arguments(argv)

    if args.version:
        print(__version__)
        return

    config = config_schema.load_config(args.configuration_file)
    keyring = Keyring(config.pop("keyring")["username"])
    ynab = YNAB.from_config(config["ynab"], keyring)
    targets = [_construct_target(c, keyring) for c in config["banks"]]

    for bank, budget_id, account_id in targets:
        print(f"Downloading transactions from {bank.full_name}")
        transaction_store = TransactionStore()
        _fetch_transactions_from_bank(
            bank, args.headless, args.no_cleanup, transaction_store
        )

        if transaction_store.count() <= 0:
            print("No transaction to push")
        else:
            print(f"Pushing {transaction_store.count()} transactions to YNAB")
            response = ynab.push(transaction_store, account_id, budget_id)
            if args.verbose:
                pprint(response.json())

            print(f"Checking for mismatches")
            ynab_transaction_store = ynab.get(account_id, budget_id)
            with open("/tmp/ynab.json", "w") as file:
                json.dump(ynab_transaction_store.json(account_id), file)
            only_on_ynab, only_in_bank = transactions_difference(
                ynab_transaction_store.transactions, transaction_store.transactions
            )

            # ignore differences that are too old
            cutoff_date = date.today() - timedelta(
                days=BANK_DATE_RANGE - MAX_COMPARE_DAYS
            )
            only_on_ynab = [t for t in only_on_ynab if t.date > cutoff_date]
            only_in_bank = [t for t in only_in_bank if t.date > cutoff_date]

            # print any differences to the console
            if only_on_ynab:
                print("Extraneous in YNAB:")
                print(pretty_format_transactions(only_on_ynab))

            if only_in_bank:
                print("Missing from YNAB:")
                print(pretty_format_transactions(only_in_bank))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
