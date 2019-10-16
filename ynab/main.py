#! /usr/bin/env python3
"""
Pull down and import transaction histories into ynab.
"""

import argparse
import os
import shutil
import sys
import tempfile
from collections import namedtuple
from pprint import pprint

from selenium.common.exceptions import TimeoutException, WebDriverException

from ynab import __version__

from . import config_schema
from .api import YNAB
from .chrome import Chrome
from .secrets import Keyring

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
    bank: Target, headless: bool, no_cleanup: bool, ynab: YNAB
):
    download_directory = tempfile.mkdtemp(dir=TEMPORARY_DIRECTORY_PARENT)
    driver = Chrome.construct(download_directory, headless)

    try:
        bank.fetch_transactions(driver, ynab, download_directory)
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
        ynab.set_default("account_id", account_id)
        _fetch_transactions_from_bank(bank, args.headless, args.no_cleanup, ynab)
        print(f"Pushing {ynab.count()} transactions to YNAB")
        response = ynab.push(budget_id)
        if args.verbose:
            pprint(response.json())


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
