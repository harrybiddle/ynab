import os
import unittest

import yaml

from ynab import config_schema

class TestConfig(unittest.TestCase):
    ''' Tests the parsing of configuration files '''

    def test_parse_example_config(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        example_config_file = os.path.join(script_dir, 'ynab.conf')
        with open(example_config_file) as f:
            as_yaml = yaml.load(f)
        validated_yaml = config_schema.parse_config(as_yaml)
        self.assertEqual(as_yaml, validated_yaml)
