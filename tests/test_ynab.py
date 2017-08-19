import os
import unittest
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

if __name__ == '__main__':
    unittest.main()
