import unittest
from tempfile import NamedTemporaryFile

import yaml
from mock import patch
from schema import SchemaError

from tests.test_config_schema import PATH_TO_TEST_CONFIG
from ynab import main


def Any(cls):
    class Any(cls):
        def __eq__(self, other):
            return True

    return Any()


class MockSchemaError(SchemaError):
    def __init__(self):
        SchemaError.__init__(self, None)


class TestMain(unittest.TestCase):
    @staticmethod
    def _run_main_with_no_banks(extra_config={}):
        with open(PATH_TO_TEST_CONFIG) as f:
            no_bank_config = yaml.safe_load(f)
        no_bank_config["banks"] = []
        no_bank_config.update(extra_config)

        with NamedTemporaryFile("w") as f:
            yaml.dump(no_bank_config, stream=f)
            f.flush()
            with patch("keyring.get_password"):
                main.main([f.name])

    def test_no_banks_is_a_no_op(self):
        self._run_main_with_no_banks()

    @patch("ynab.config_schema.parse_config", side_effect=MockSchemaError)
    def test_schema_error_aborts_main(self, _):
        with self.assertRaises(SchemaError):
            self._run_main_with_no_banks()


if __name__ == "__main__":
    unittest.main()
