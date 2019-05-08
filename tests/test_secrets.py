import unittest
from collections import defaultdict

from mock import patch

from ynab.secrets import Keyring

SECRET_NAME1 = "password"
SECRET_NAME2 = "pin"
SECRET_KEY1 = "ynab_password"
SECRET_KEY2 = "ynab_pin"
SECRET_VALUE1 = "pass123"
SECRET_VALUE2 = 1234
USERNAME = "johnsnow"
SECRETS_KEYS_CONFIG = {SECRET_NAME1: SECRET_KEY1, SECRET_NAME2: SECRET_KEY2}
SECRETS = {SECRET_NAME1: SECRET_VALUE1, SECRET_NAME2: SECRET_VALUE2}


def mock_keyring_get_password(service_name, username):
    """ A mock for keyring.get_password """
    expected_values = {
        (SECRET_KEY1, USERNAME): SECRET_VALUE1,
        (SECRET_KEY2, USERNAME): SECRET_VALUE2,
    }
    d = defaultdict(None, expected_values)
    return d[(service_name, username)]


class TestKering(unittest.TestCase):
    """ Tests the part of the code that fetches secrets from the keyring """

    # Tests ############################################################################

    def test_empty_dictionary(self):
        self.assertEqual({}, self.call_get_secrets_from_keyring({}))

    @patch("keyring.get_password")
    def test_raises_when_key_doesnt_exist(self, keyring):
        keyring.side_effect = mock_keyring_get_password
        with self.assertRaises(KeyError):
            self.call_get_secrets_from_keyring({"foo": "bar"})

    @patch("keyring.get_password")
    def test_fetches_all_secrets(self, keyring):
        keyring.side_effect = mock_keyring_get_password
        secrets = self.call_get_secrets_from_keyring(SECRETS_KEYS_CONFIG)
        self.assertEqual(SECRETS, secrets)

    # Helpers ##########################################################################

    def call_get_secrets_from_keyring(self, secrets):
        keyring = Keyring(USERNAME)
        return keyring.get_secrets(secrets)
