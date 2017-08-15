#! /usr/bin/env python

import argparse
import collections
import os
import shutil
import sys
import yaml
import tempfile

from selenium import webdriver

import natwest_com as Natwest
from amex_com import Amex
from halifax_com import Halifax
from hsbc_com import HSBC
import youneedabudget_com as ynab

from schema import Schema, And, Or, Use, Optional, SchemaError

_SOURCE_TYPES = {'natwest': lambda x: x}

_SOURCE_SCHEMA = {'type': Or(*_SOURCE_TYPES.keys()),
                  Optional('target_id'): object,
                  Optional('id'): object}
_TARGET_SCHEMA = {'budget': And(str, len),
                  'account': And(str, len),
                  'id': object}
_YNAB_SCHEMA = {'email': And(str, len),
                Optional('targets'): [_TARGET_SCHEMA]}
_CONFIG_SCHEMA = Schema({'sources': [_SOURCE_SCHEMA],
                         Optional('ynab'): _YNAB_SCHEMA})

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

def construct_source_objects(configs):
    def construct_object(config):
        source_type = config['type']
        source_class = _SOURCE_TYPES[source_type]
        return source_class(config)
    return map(construct_object, configs)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = getArgParser()
    args = parser.parse_args(argv)

    loaded_config = yaml.load(args.configuration_file)
    config = parse_config(loaded_config)

    print "Fetching recent transactions from " + args.bank[0]

    bank = None
    if (args.bank[0] == 'amex'):
        bank = Amex()
    elif (args.bank[0] == 'halifax'):
        bank = Halifax()
    elif (args.bank[0] == 'hsbc'):
        bank = HSBC()
    elif (args.bank[0] == 'natwest'):
        bank = Natwest()

    bank.get_secret_text_from_user()

    # For now, only support exactly one source and one target #################
    # TODO expand on this
    source_configs = config['sources']
    _ = construct_source_objects(source_configs)  # unused for now
    assert(len(source_configs) == 1)
    assert('ynab' in config)
    ynab_config = config['ynab']
    assert('targets' in ynab_config)
    target_configs = ynab_config['targets']
    assert(len(target_configs) == 1)
    target_config = target_configs[0]
    assert(source_configs[0]['target_id'] == target_config['id'])
    email = ynab_config['email']
    ###########################################################################

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
        ynab.upload_transactions(bank, driver, path, target_config, email)

        print "Removing the remaints"
        shutil.rmtree(temp_download_dir)
    finally:
        if not args.open:
            driver.quit()
        if os.path.exists(temp_download_dir):
            sys.stderr.write(('Temporary directory not removed: {}\n'
                              .format(temp_download_dir)))

def getArgParser():
    parser = argparse.ArgumentParser(description='Pull down and import transaction histories into ynab.')
    parser.add_argument('-b', '--bank', nargs=1, choices=['natwest', 'amex', 'halifax', 'hsbc'], required=True,
                        help='The bank you would like to pull transactions from')

    # TODO(jboreiko) not functional currently :(
    parser.add_argument('-o', '--open', action='store_true', help='If you would like to keep the tabs open')
    parser.add_argument('configuration_file', type=argparse.FileType('r'))
    return parser

if __name__ == '__main__':
    main()
