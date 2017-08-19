import os
import unittest
import yaml
from schema import SchemaError

from ynab import ynab


class TestConfig(unittest.TestCase):
    def _create_source(self, id=None):
        some_valid_type = ynab._SOURCE_TYPES.keys()[0]
        d = {'type': some_valid_type}
        if id:
            d['id'] = id
        return d

    def _parse_config(self, sources=[]):
        config = {'sources': sources}
        ynab.parse_config(config)

    def _expected_failure(*args, **kwargs):
        with args[0].assertRaises(SchemaError):
            args[0]._parse_config(*args[1:], **kwargs)

    def _expected_success(*args, **kwargs):
        args[0]._parse_config(*args[1:], **kwargs)

    def test_suceess_if_only_sources(self):
        s = self._create_source()
        self._expected_success(sources=[s])

    def test_parse_example_config(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        example_config_file = os.path.join(script_dir, 'ynab.conf')
        with open(example_config_file) as f:
            as_yaml = yaml.load(f)
        validated_yaml = ynab.parse_config(as_yaml)
        self.assertEqual(as_yaml, validated_yaml)

if __name__ == '__main__':
    unittest.main()
