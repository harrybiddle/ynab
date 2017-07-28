import os
import sys
import unittest
import commentjson

from ynab import ynab

_ID = '1234768965'
_PIN = '9750'
_PASSWORD1 = 'mycrazyp!asswithatleasttencharacters'
_EMAIL = 'who@you.com'
_PASSWORD2 = 'myothercrazypas8s'


class TestSecret(unittest.TestCase):
    def test_valid_construction(self):
        secret_text = ';'.join([_ID, _PIN, _PASSWORD1, _EMAIL, _PASSWORD2])
        s = ynab.parse_secret(secret_text)
        self.assertEqual(s.customer_number, _ID)
        self.assertEqual(s.pin, _PIN)
        self.assertEqual(s.natwest_password, _PASSWORD1)
        self.assertEqual(s.email, _EMAIL)
        self.assertEqual(s.ynab_password, _PASSWORD2)


if __name__ == '__main__':
    unittest.main()
