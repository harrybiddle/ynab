import os
import unittest
import commentjson

from ynab import ynab
from ynab import natwest_com as natwest

import website_mock as wm

_ID = '1234768965'
_PIN = '9750'
_PASSWORD1 = 'mycrazyp!asswithatleasttencharacters'
_EMAIL = 'who@you.com'
_PASSWORD2 = 'myothercrazypas8s'

natwest_mock = os.path.join(os.path.dirname(__file__), 'natwest_mock.json')

class TestSelectCharacters(unittest.TestCase):
    def test_happy_path(self):
        secret = ynab.Secret(_ID, _PIN, _PASSWORD1, _EMAIL, _PASSWORD2)

        pin_digits = ['Enter the 4th number',
                      'Enter the 2nd number',
                      'Enter the 3rd number']
        password_chars = ['Enter the 5th character',
                          'Enter the 7th character',
                          'Enter the 10th character']

        a, b = natwest._select_characters(secret, pin_digits, password_chars)
        self.assertEqual(a, _PIN[3] + _PIN[1] + _PIN[2])
        self.assertEqual(b, _PASSWORD1[4] + _PASSWORD1[6] + _PASSWORD1[9])


class TestNatwestWebsiteDefinition(unittest.TestCase):
    def test_natwest_definition_valid(self):
        with open(natwest_mock) as file:
            js = commentjson.load(file)
            wm.WebsiteDefinition(js)


class TestNatwest(unittest.TestCase):
    def test_download_transactions(self):
        secret = ynab.Secret(_ID, _PIN, _PASSWORD1, _EMAIL, _PASSWORD2)
        driver = wm.WebsiteMock.fromfile(natwest_mock)
        natwest.download_transactions(secret, driver, select=wm.Select)


if __name__ == '__main__':
    unittest.main()
