#! /usr/bin/env python
''' Pull down and import transaction histories into ynab.
'''

import argparse
from collections import OrderedDict
import os
import shutil
import sys
import tempfile
import yaml

from selenium import webdriver
from getpass import getpass

from natwest_com import Natwest
from amex_com import Amex
from halifax_com import Halifax
from hsbc_com import HSBC
import youneedabudget_com as ynab
from bank import Bank

from schema import Schema, And, Or, Optional

_BANKS = {'amex': Amex,
          'halifax': Halifax,
          'hsbc': HSBC,
          'natwest': Natwest}

_SOURCE_SCHEMA = {'type': Or(*_BANKS.keys()),
                  Optional('target_id'): object}
_TARGET_SCHEMA = {'budget': And(str, len),
                  'account': And(str, len),
                  Optional('id'): object}
_YNAB_SCHEMA = {'email': And(str, len),
                'targets': [_TARGET_SCHEMA]}
_CONFIG_SCHEMA = Schema({'sources': [_SOURCE_SCHEMA],
                         'ynab': _YNAB_SCHEMA})

def make_temp_download_dir():
    user_download_directory = os.path.expanduser('~/Downloads/')
    return tempfile.mkdtemp(dir=user_download_directory)

def chrome_driver(temp_download_dir):
    options = webdriver.chrome.options.Options()
    prefs = {'download.default_directory': temp_download_dir}
    options.add_experimental_option('prefs', prefs)
    return webdriver.Chrome(chrome_options=options)

def parse_config(config):
    return _CONFIG_SCHEMA.validate(config)

def construct_banks_from_config(configs):
    def construct_object(config):
        source_type = config['type']
        source_class = _BANKS[source_type]
        return source_class(config)
    return map(construct_object, configs)

def get_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration_file', type=argparse.FileType('r'))
    return parser

def get_all_secrets_from_user(required_secrets, getpass=getpass):
    ret = OrderedDict()
    prompt = 'Enter a semicolon-separated list of:\n'
    for bank, secrets in required_secrets.iteritems():
        for secret in secrets:
            prompt = prompt + '\t{} {}\n'.format(bank.full_name, secret)
    sys.stdout.write(prompt)
    user_inputs = getpass()
    inputted_secrets = user_inputs.split(';')
    assert (len(inputted_secrets) == sum([len(secrets) for secrets in required_secrets.values()]))
    ret = {}
    i = 0
    for bank, secrets in required_secrets.iteritems():
        d = {}
        for secret in secrets:
            d[secret] = inputted_secrets[i]
            i = i + 1
        ret[bank] = d
    return ret

class YNAB(Bank):

    full_name = 'YNAB'

    def __init__(self, config):
        super(YNAB, self).__init__(['password'])
        self.email = config['email']

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_argument_parser()
    args = parser.parse_args(argv)

    loaded_config = yaml.load(args.configuration_file)
    config = parse_config(loaded_config)

    y = YNAB(config['ynab'])
    banks = construct_banks_from_config(config['sources'])

    # For now, only support one source and one target
    bank = banks[0]
    print 'Fetching recent transactions from {}'.format(bank.full_name)

    # get all secrets from user
    required_secrets = OrderedDict([(b, b.all_secrets) for b in banks + [y]])
    for t in required_secrets.iteritems():
        print t
    secrets = get_all_secrets_from_user(required_secrets)

    # pass them back to the banks (and ynab)
    for b, s in secrets.iteritems():
        b.extract_secrets(s)

    print 'Starting chrome to do your bidding'
    temp_download_dir = make_temp_download_dir()
    driver = chrome_driver(temp_download_dir)
    driver.implicitly_wait(10)

    try:
        print 'Downloading transactions from ' + bank.full_name
        path = bank.download_transactions(driver, temp_download_dir)

        driver.execute_script('window.open(\'about:blank\', \'_blank\');')
        driver.switch_to_window(driver.window_handles[1])

        print 'Uploading transactions to ynab'
        ynab.upload_transactions(bank, driver, [path], target_config, email)

        print 'Removing the remaints'
        shutil.rmtree(temp_download_dir)
    finally:
        driver.quit()
        if os.path.exists(temp_download_dir):
            sys.stderr.write(('Temporary directory not removed: {}\n'
                              .format(temp_download_dir)))

if __name__ == '__main__':
    main()
