#! /usr/bin/env python

import argparse
import collections
import shutil
import sys
import tempfile
import argparse
import os

from selenium import webdriver

import natwest_com as natwest
from amex_com import Amex
from halifax_com import Halifax
from hsbc_com import HSBC
import youneedabudget_com as ynab

def make_temp_download_dir():
    user_download_directory = os.path.expanduser('~/Downloads/')
    return tempfile.mkdtemp(dir=user_download_directory)

def chrome_driver(temp_download_dir):
    options = webdriver.chrome.options.Options()
    prefs = {'download.default_directory': temp_download_dir}
    options.add_experimental_option('prefs', prefs)
    return webdriver.Chrome(chrome_options=options)

def main(argv):
    print "Fetching recent transactions from " + argv.bank[0]

    bank = None
    if (argv.bank[0] == 'amex'):
        bank = Amex()
    elif (argv.bank[0] == 'halifax'):
        bank = Halifax()
    elif (argv.bank[0] == 'hsbc'):
        bank = HSBC()
    elif (argv.bank[0] == 'natwest'):
        raise NotImplementedError("Not done for natwest")

    bank.get_secret_text_from_user()

    print "Starting chrome to do your bidding"
    temp_download_dir = make_temp_download_dir()
    driver = chrome_driver(temp_download_dir)
    driver.implicitly_wait(10)

    try:
        print "Downloading transactions from " + bank.full_name
        path = bank.download_transactions(driver, temp_download_dir)

        driver.execute_script('''window.open("about:blank", "_blank");''')
        driver.switch_to_window(driver.window_handles[1])

        print "Uploading transactions to ynab"
        ynab.upload_transactions(bank, driver, path)

        print "Removing the remaints"
        shutil.rmtree(temp_download_dir)
    finally:
        if not argv.open:
            driver.quit()
        if os.path.exists(temp_download_dir):
            sys.stderr.write(('Temporary directory not removed: {}\n'
                              .format(temp_download_dir)))

def getArgParser():
    parser = argparse.ArgumentParser(description='Pull down and import transaction histories into ynab.')
    parser.add_argument('-b', '--bank', nargs=1, choices=['natwest', 'amex', 'halifax', 'hsbc'], required=True,
                        help='The bank you would like to pull transactions from')
    parser.add_argument('-o', '--open', action='store_true', help='If you would like to keep the tabs open')
    return parser

if __name__ == '__main__':
    parser = getArgParser()
    sys.exit(main(parser.parse_args()))
