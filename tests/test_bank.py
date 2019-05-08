import unittest

from ynab import bank


class TestSecrets(unittest.TestCase):
    def setUp(self):
        secrets = {"password": "pass123", "pin": 1234}
        self.bank = bank.Bank(secrets)

    def test_validate_secrets_success(self):
        self.bank.validate_secrets("password", "pin")

    def test_validate_unrecognised_secret_fails(self):
        with self.assertRaises(AssertionError):
            self.bank.validate_secrets("password", "foo")

    def test_validate_too_few_secrets_fails(self):
        with self.assertRaises(AssertionError):
            self.bank.validate_secrets("password")

    def test_secret_lookup_success(self):
        self.assertEqual("pass123", self.bank.secret("password"))
        self.assertEqual(1234, self.bank.secret("pin"))

    def test_secret_lookup_failure(self):
        with self.assertRaises(KeyError):
            self.bank.secret("foo")


if __name__ == "__main__":
    unittest.main()
