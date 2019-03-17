import os
import unittest

import yaml

from ynab import config_schema

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PATH_TO_TEST_CONFIG = os.path.join(_SCRIPT_DIR, "ynab.conf")


class TestConfig(unittest.TestCase):
    """ Tests the parsing of configuration files """

    def test_parse_example_config(self):
        with open(PATH_TO_TEST_CONFIG) as f:
            as_yaml = yaml.load(f)
        validated_yaml = config_schema.parse_config(as_yaml)
        self.assertEqual(as_yaml, validated_yaml)
