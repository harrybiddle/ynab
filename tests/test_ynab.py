import os
import unittest
from collections import OrderedDict
from mock import MagicMock
import yaml
from schema import SchemaError

from ynab import ynab

class TestConfig(unittest.TestCase):
    def test_parse_example_config(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        example_config_file = os.path.join(script_dir, 'ynab.conf')
        with open(example_config_file) as f:
            as_yaml = yaml.load(f)
        validated_yaml = ynab.parse_config(as_yaml)
        self.assertEqual(as_yaml, validated_yaml)

class TestYnab(unittest.TestCase):
    def test_get_one_secret(self):
        bank = type('', (), {})
        bank.full_name = 'MyBank'
        getpass = MagicMock(return_value='pass123')
        required_secrets = OrderedDict({bank: ['password']})
        secrets = ynab.get_all_secrets_from_user(required_secrets, getpass=getpass)
        self.assertEqual(secrets, OrderedDict({bank: {'password': 'pass123'}}))

    def test_get_two_secrets(self):
        bank = type('', (), {})
        bank.full_name = 'MyBank1'
        bank2 = type('', (), {})
        bank2.full_name = 'MyBank2'
        getpass = MagicMock(return_value='pass123;pass456')
        required_secrets = OrderedDict()
        required_secrets[bank] = ['password']
        required_secrets[bank2] = ['pin']
        for a,b in required_secrets.iteritems():
            print a.full_name,b
        secrets = ynab.get_all_secrets_from_user(required_secrets, getpass=getpass)
        expected_result = OrderedDict()
        expected_result[bank] = {'password': 'pass123'}
        expected_result[bank2] = {'pin': 'pass456'}
        self.assertEqual(secrets, expected_result)

if __name__ == '__main__':
    unittest.main()
