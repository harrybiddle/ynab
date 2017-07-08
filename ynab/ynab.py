#! /usr/bin/env python

import collections
import os.path
import shutil
import sys
import tempfile
from glob import glob
import time
from getpass import getpass
from selenium import webdriver
from polling import poll

import natwest_com as natwest
import youneedabudget_com as ynab

Secret = collections.namedtuple('Secret', ('customer_number pin '
                                           'natwest_password email '
                                           'ynab_password'))

_WAIT_FOR_OFX_DOWNLOAD_SECONDS = 10
_WAIT_FOR_OFX_DOWNLOAD_POLL_SECONDS = 1


def parse_secret(semicolon_separated_text):
    return Secret(*semicolon_separated_text.split(';'))


def parse_secret_text_from_user():
    ''' Prompts the user to enter the secret text and returns their entry'''
    sys.stdout.write ('Enter a comma-separated list of customer number, pin, '
                      'natwest password, email, YNAB password: ')
    user_input = getpass()
    return parse_secret(user_input)


def make_temp_download_dir():
    user_download_directory = os.path.expanduser('~/Downloads/')
    return tempfile.mkdtemp(dir=user_download_directory)


def chrome_driver(temp_download_dir):
    options = webdriver.chrome.options.Options();
    prefs = {'download.default_directory': temp_download_dir}
    options.add_experimental_option('prefs', prefs)
    return webdriver.Chrome(chrome_options=options)


def wait_until_ofx_file_in_dir(dir):
    ''' Waits for _WAIT_FOR_OFX_DOWNLOAD_SECONDS seconds until a
    *.ofx file exists in the given directory. When it does, returns
    the full file path to that file, or the first file if there are
    many
    '''
    g = os.path.join(dir, '*.ofx')
    poll(lambda: glob(g),
         timeout=_WAIT_FOR_OFX_DOWNLOAD_SECONDS,
         step=_WAIT_FOR_OFX_DOWNLOAD_POLL_SECONDS)
    return glob(g)[0]


def main():
    secret = parse_secret_text_from_user()
    temp_download_dir = make_temp_download_dir()
    driver = chrome_driver(temp_download_dir)

    try:
        natwest.download_transactions(secret, driver)
        path = wait_until_ofx_file_in_dir(temp_download_dir)
        ynab.upload_transactions(secret, driver, path)
        shutil.rmtree(temp_download_dir)
    finally:
        driver.quit()
        if os.path.exists(temp_download_dir):
            sys.stderr.write(('Temporary directory not removed: {}\n'
                              .format(temp_download_dir)))


if __name__ == '__main__':
    sys.exit(main())
