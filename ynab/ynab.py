#! /usr/bin/env python
''' Pull down and import transaction histories into ynab.
'''

import argparse
import os
import shutil
import sys
import tempfile
from datetime import datetime

from polling import TimeoutException
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import keyring_secrets
import config_schema

from youneedabudget_com import YNAB

TEMPORARY_DIRECTORY = '~/Downloads'


def chrome_driver(temp_download_dir, headless=False):
    options = webdriver.chrome.options.Options()
    prefs = {'download.default_directory': temp_download_dir}
    options.add_experimental_option('prefs', prefs)
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    return webdriver.Chrome(chrome_options=options)


def copy_without_key(d, key_to_skip):
    ''' Returns a copy of the dictionary d, except without one specified key
    '''
    return {i: d[i] for i in d if i != key_to_skip}


def fetch_secrets_and_construct_bank(class_, config, keyring_username):
    secrets_keys = config.get('secrets_keys', {})
    secrets = keyring_secrets.get_secrets(secrets_keys, keyring_username)
    config_without_secrets_keys = copy_without_key(config, 'secrets_keys')
    return class_(config_without_secrets_keys, secrets)


def fetch_secrets_and_construct_banks(configs, keyring_username):
    ''' Takes a list of source configurations and constructs Banks objects
    according to the 'types' dictionary. As part of this, the keyring will be
    queried for any required secrets.
    '''
    def construct(config):
        bank_type = config['type']
        class_ = config_schema.BANKS[bank_type]
        return fetch_secrets_and_construct_bank(class_, config,
                                                keyring_username)
    return [construct(c) for c in configs]


def take_screenshot(driver):
    directory = tempfile.gettempdir()
    basename = datetime.now().strftime('%d-%b-%y-%H:%m:%S')
    filename = '{}.png'.format(basename)
    path = os.path.join(directory, filename)
    driver.get_screenshot_as_file(path)
    print('Screenshot saved as {}'.format(path))


def get_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration_file', type=str,
                        default=os.path.expanduser('~/.ynab.conf'), nargs='?',
                        help='defaults to ~/.ynab.conf')
    parser.add_argument('--headless', action='store_true',
                        help='Do not open a visible browser window')
    parser.add_argument('--screenshot', action='store_true',
                        help='Save screenshots on failure')
    return parser


def quit_driver_continue_on_exception(driver):
    try:
        driver.quit()
        return 0
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        return 1


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_argument_parser()
    args = parser.parse_args(argv)

    config = config_schema.load_config(args.configuration_file)

    # construct banks
    keyring_username = config['keyring']['username']
    banks = fetch_secrets_and_construct_banks(config['sources'],
                                              keyring_username)

    # construct ynab
    ynab = fetch_secrets_and_construct_bank(YNAB, config['ynab'],
                                            keyring_username)

    # exit if no banks
    if not banks:
        return

    # For now, only support one source and one target
    bank = banks[0]

    p = os.path.expanduser(TEMPORARY_DIRECTORY)
    temp_download_dir = tempfile.mkdtemp(dir=p)
    driver = chrome_driver(temp_download_dir, args.headless)
    driver.implicitly_wait(10)

    try:
        print('Downloading transactions from ' + bank.full_name)
        path = bank.download_transactions(driver, temp_download_dir)

        driver.execute_script('window.open(\'about:blank\', \'_blank\');')
        driver.switch_to_window(driver.window_handles[1])

        print('Uploading transactions to ynab')
        ynab.upload_transactions(bank, driver, [path])
    except (TimeoutException, WebDriverException):
        if args.screenshot:
            take_screenshot(driver)
        raise
    finally:
        ret_code = quit_driver_continue_on_exception(driver)

        print('Removing the remaints')
        if os.path.exists(temp_download_dir):
            shutil.rmtree(temp_download_dir)

    return ret_code


if __name__ == '__main__':
    main()
