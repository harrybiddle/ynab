#! /usr/bin/env python
''' Pull down and import transaction histories into ynab.
'''

from collections import OrderedDict
import argparse
import os
import shutil
import sys
import tempfile

from selenium import webdriver
import keyring_secrets
import yaml

from amex_com import Amex
from bank import Bank
from halifax_com import Halifax
from hsbc_com import HSBC
from natwest_com import Natwest
from youneedabudget_com import YNAB

from schema import Schema, And, Or, Optional

_BANKS = {'amex': Amex,
          'halifax': Halifax,
          'hsbc': HSBC,
          'natwest': Natwest}

_SOURCE_SCHEMA = {'type': Or(*_BANKS.keys()),
                  Optional('secrets_keys'): {str: str},
                  Optional(str): object}
_TARGET_SCHEMA = {'budget': And(str, len),
                  'account': And(str, len),
                  Optional('id'): object}
_YNAB_SCHEMA = {'email': And(str, len),
                'targets': [_TARGET_SCHEMA],
                'secrets_keys': {'password': str}}
_KEYRING_SCHEMA = {'username': str}
_CONFIG_SCHEMA = Schema({'sources': [_SOURCE_SCHEMA],
                         'ynab': _YNAB_SCHEMA,
                         'keyring': _KEYRING_SCHEMA})

TEMPORARY_DIRECTORY = '~/Downloads'


def chrome_driver(temp_download_dir):
    options = webdriver.chrome.options.Options()
    prefs = {'download.default_directory': temp_download_dir}
    options.add_experimental_option('prefs', prefs)
    return webdriver.Chrome(chrome_options=options)

def parse_config(config):
    ''' Raises: SchemaError if the supplied configuration is invalid
    '''
    return _CONFIG_SCHEMA.validate(config)

def copy_without_key(d, key_to_skip):
    ''' Returns a copy of the dictionary d, except without one specified key '''
    return {i:d[i] for i in d if i != key_to_skip}

def fetch_secrets_and_construct_bank(clazz, config, keyring_username):
    secrets_keys = config.get('secrets_keys', {})
    secrets = keyring_secrets.get_secrets(secrets_keys, keyring_username)
    config_without_secrets_keys = copy_without_key(config, 'secrets_keys')
    return clazz(config_without_secrets_keys, secrets)

def fetch_secrets_and_construct_banks(configs, keyring_username):
    ''' Takes a list of source configurations and constructs Banks objects
    according to the 'types' dictionary. As part of this, the keyring will be
    queried for any required secrets.
    '''
    def construct(config):
        bank_type = config['type']
        clazz = _BANKS[bank_type]
        return fetch_secrets_and_construct_bank(clazz, config, keyring_username)
    return map(construct, configs)

def get_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration_file', type=str,
                        default=os.path.expanduser('~/.ynab.conf'), nargs='?',
                        help='defaults to ~/.ynab.conf')
    return parser

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_argument_parser()
    args = parser.parse_args(argv)

    with open(args.configuration_file) as conf:
        loaded_config = yaml.load(conf)
    config = parse_config(loaded_config)

    # construct banks
    keyring_username = config['keyring']['username']
    banks = fetch_secrets_and_construct_banks(config['sources'], keyring_username)

    # construct ynab
    ynab = fetch_secrets_and_construct_bank(YNAB, config['ynab'], keyring_username)

    # For now, only support one source and one target
    bank = banks[0]

    print 'Starting chrome to do your bidding'
    temp_download_dir = tempfile.mkdtemp(dir=os.path.expanduser(TEMPORARY_DIRECTORY))
    driver = chrome_driver(temp_download_dir)
    driver.implicitly_wait(10)

    try:
        print 'Downloading transactions from ' + bank.full_name
        path = bank.download_transactions(driver, temp_download_dir)

        driver.execute_script('window.open(\'about:blank\', \'_blank\');')
        driver.switch_to_window(driver.window_handles[1])

        print 'Uploading transactions to ynab'
        ynab.upload_transactions(bank, driver, [path])

        print 'Removing the remaints'
        shutil.rmtree(temp_download_dir)
    finally:
        driver.quit()
        if os.path.exists(temp_download_dir):
            sys.stderr.write(('Temporary directory not removed: {}\n'
                              .format(temp_download_dir)))

    return 0

if __name__ == '__main__':
    main()
