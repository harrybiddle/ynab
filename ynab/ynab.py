#! /usr/bin/env python
''' Pull down and import transaction histories into ynab.
'''

from collections import OrderedDict
import argparse
import os
import shutil
import sys
import tempfile
import yaml

from getpass import getpass
from selenium import webdriver

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
                  str: object}
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
    ''' Raises: SchemaError if the supplied configuration is invalid
    '''
    return _CONFIG_SCHEMA.validate(config)

def construct_banks_from_config(configs):
    ''' Takes source configuration and returns a list of Bank objects
    constructed from it.
    '''
    def construct_object(config):
        source_type = config['type']
        source_class = _BANKS[source_type]
        return source_class(config)
    return map(construct_object, configs)

def get_all_secrets_from_user(required_secrets, getpass=getpass):
    ''' Given a dictionary mapping a Bank object to a list of names of secrets,
    we ask the user to supply _all_ of the given secrets as a semi-colon
    separated list. The input dictionary should be ordered, as they are
    requested from the user in the order supplied. Returns a map of Bank to
    a map of secret name -> supplied value; with the banks in the same order
    as supplied.

    For example, given this input:

        {Bank1: ['password', 'pin'],
         Bank2: ['password']}

    The user will be asked to provide a semi-colon separated list of
    Bank1/password, Bank1/pin, Bank2/password. If they were to supply

        'apples;1234;oranges'

    Then the return value would be

        {Bank1: {'password': 'apples',
                 'pin': '1234'},
         Bank2: {'password': 'oranges'}}
    '''
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

def fetch_secrets(banks):
    ''' Receives a list of Bank objects, and constructs a list of the total
    secrets required by all of them. We fetch these secrets from the user,
    then pass them to the Bank objects. Upon function exit the Bank objects
    will therefore be endowed with the secrets they require. When the user
    is prompted for the secrets, they will be prompted in the order that the
    Banks were given to this function, so ensure that the iterable is ordered
    '''
    required_secrets = OrderedDict([(b, b.all_secrets) for b in banks])
    for t in required_secrets.iteritems():
        print t
    secrets = get_all_secrets_from_user(required_secrets)
    for b, s in secrets.iteritems():
        b.extract_secrets(s)

def get_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration_file', type=argparse.FileType('r'))
    return parser

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_argument_parser()
    args = parser.parse_args(argv)

    loaded_config = yaml.load(args.configuration_file)
    config = parse_config(loaded_config)

    ynab = YNAB(config['ynab'])
    banks = construct_banks_from_config(config['sources'])

    # For now, only support one source and one target
    bank = banks[0]
    print 'Fetching recent transactions from {}'.format(bank.full_name)

    fetch_secrets([bank, ynab])

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
        ynab.upload_transactions(bank, driver, [path])

        print 'Removing the remaints'
        shutil.rmtree(temp_download_dir)
    finally:
        driver.quit()
        if os.path.exists(temp_download_dir):
            sys.stderr.write(('Temporary directory not removed: {}\n'
                              .format(temp_download_dir)))

if __name__ == '__main__':
    main()
