#! /usr/bin/env python

import argparse
import collections
import os.path
import shutil
import sys
import yaml
import tempfile
from glob import glob
import time
from getpass import getpass
from selenium import webdriver
from polling import poll

import natwest_com as natwest
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

Secret = collections.namedtuple('Secret', ('customer_number pin '
                                           'natwest_password '
                                           'ynab_password'))

_WAIT_FOR_OFX_DOWNLOAD_SECONDS = 10
_WAIT_FOR_OFX_DOWNLOAD_POLL_SECONDS = 1


def parse_secret(semicolon_separated_text):
    return Secret(*semicolon_separated_text.split(';'))


def parse_secret_text_from_user():
    ''' Prompts the user to enter the secret text and returns their entry'''
    sys.stdout.write('Enter a comma-separated list of customer number, pin, '
                     'natwest password, YNAB password: ')
    user_input = getpass()
    return parse_secret(user_input)


def make_temp_download_dir():
    user_download_directory = os.path.expanduser('~/Downloads/')
    return tempfile.mkdtemp(dir=user_download_directory)


def chrome_driver(temp_download_dir):
    options = webdriver.chrome.options.Options()
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


def parse_config(config):
    return _CONFIG_SCHEMA.validate(config)


def construct_source_objects(configs):
    def construct_object(config):
        source_type = config['type']
        source_class = _SOURCE_TYPES[source_type]
        return source_class(config)
    return map(construct_object, configs)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_file', type=argparse.FileType('r'))
    args = parser.parse_args(argv[1:])

    loaded_config = yaml.load(args.configuration_file)
    config = parse_config(loaded_config)

    secret = parse_secret_text_from_user()

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

    temp_download_dir = make_temp_download_dir()
    driver = chrome_driver(temp_download_dir)

    try:
        natwest.download_transactions(secret, driver)
        path = wait_until_ofx_file_in_dir(temp_download_dir)
        ynab.upload_transactions(secret, driver, path, target_config, email)
        shutil.rmtree(temp_download_dir)
    finally:
        driver.quit()
        if os.path.exists(temp_download_dir):
            sys.stderr.write(('Temporary directory not removed: {}\n'
                              .format(temp_download_dir)))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
