import os
import unittest
from collections import defaultdict

from mock import patch, MagicMock
import yaml

from ynab import ynab

SECRET_NAME1 = 'password'
SECRET_NAME2 = 'pin'
SECRET_KEY1 = 'ynab_password'
SECRET_KEY2 = 'ynab_pin'
SECRET_VALUE1 = 'pass123'
SECRET_VALUE2 = 1234
USERNAME = 'johnsnow'

SECRETS_KEYS_CONFIG = {
    SECRET_NAME1: SECRET_KEY1,
    SECRET_NAME2: SECRET_KEY2
}

SECRETS = {
    SECRET_NAME1: SECRET_VALUE1,
    SECRET_NAME2: SECRET_VALUE2
}

def Any(cls):
    class Any(cls):
        def __eq__(self, other):
            return True
    return Any()

def mock_keyring_get_password(service_name, username):
    ''' A mock for keyring.get_password '''
    expected_values = {(SECRET_KEY1, USERNAME): SECRET_VALUE1,
                       (SECRET_KEY2, USERNAME): SECRET_VALUE2}
    d = defaultdict(None, expected_values)
    return d[(service_name, username)]

def concatd(*args):
    ''' Concatenates dictionaries together '''
    ret = {}
    for d in args:
        ret.update(d)
    return ret

class TestConfig(unittest.TestCase):
    ''' Tests the parsing of configuration files '''

    def test_parse_example_config(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        example_config_file = os.path.join(script_dir, 'ynab.conf')
        with open(example_config_file) as f:
            as_yaml = yaml.load(f)
        validated_yaml = ynab.parse_config(as_yaml)
        self.assertEqual(as_yaml, validated_yaml)


class TestGetSecretsFromKeyring(unittest.TestCase):
    ''' Tests the part of the code that fetches secrets from the keyring '''

    def call_get_secrets_from_keyring(self, secrets):
        return ynab.get_secrets_from_keyring(secrets, USERNAME)

    def test_empty_dictionary(self):
        self.assertEqual({}, self.call_get_secrets_from_keyring({}))

    @patch('keyring.get_password')
    def test_raises_when_key_doesnt_exist(self, keyring):
        keyring.side_effect = mock_keyring_get_password
        with self.assertRaises(KeyError):
            self.call_get_secrets_from_keyring({'foo': 'bar'})

    @patch('keyring.get_password')
    def test_fetches_all_secrets(self, keyring):
        keyring.side_effect = mock_keyring_get_password
        secrets = self.call_get_secrets_from_keyring(SECRETS_KEYS_CONFIG)
        self.assertEqual(SECRETS, secrets)

class TestFetchSecretsAndConstructBanks(unittest.TestCase):
    ''' Tests the part of the code that constructs Bank objects from config '''

    def setUp(self):
        self.bank_init = bank_init = MagicMock()
        class BankMock(object):
            def __init__(self, *args, **kwargs):
                bank_init(*args, **kwargs)
        self.bank_cls = BankMock
        self.bank_config = {'foo': 'bar'}

    def assert_bank_init_with_args(self, *args):
        self.bank_init.assert_called_with(*args)

    def call_fetch_secrets_and_construct_bank(self, config):
        ynab.fetch_secrets_and_construct_bank(self.bank_cls, config, USERNAME)

    @patch('keyring.get_password')
    def test_bank_recieves_config_and_secrets_minus_keys(self, keyring):
        keyring.side_effect = mock_keyring_get_password
        secrets_keys_config = {'secrets_keys': SECRETS_KEYS_CONFIG}
        config = concatd(self.bank_config, secrets_keys_config)

        self.call_fetch_secrets_and_construct_bank(config)
        self.assert_bank_init_with_args(self.bank_config, SECRETS)

    def test_bank_construction_completes_when_no_secrets_keys_config(self):
        config = self.bank_config

        self.call_fetch_secrets_and_construct_bank(config)
        self.assert_bank_init_with_args(self.bank_config, {})

    def test_bank_construction_completes_when_empty_secrets_keys_config(self):
        secrets_keys_config = {'secrets_keys': {}}
        config = concatd(self.bank_config, secrets_keys_config)

        self.call_fetch_secrets_and_construct_bank(config)
        self.assert_bank_init_with_args(self.bank_config, {})

if __name__ == '__main__':
    unittest.main()
