import unittest

from ynab import natwest_com as natwest


_ID = '1234768965'
_PIN = '9750'
_PASSWORD1 = 'mycrazyp!asswithatleasttencharacters'
_PASSWORD2 = 'myothercrazypas8s'


class TestSecret(unittest.TestCase):
    def test_valid_construction(self):
        secret_text = ';'.join([_ID, _PIN, _PASSWORD1, _PASSWORD2])
        n = natwest.Natwest()
        s = n.parse_secret(secret_text)
        self.assertEqual(s.customer_number, _ID)
        self.assertEqual(s.pin, _PIN)
        self.assertEqual(s.natwest_password, _PASSWORD1)
        self.assertEqual(s.ynab_password, _PASSWORD2)

class TestSelectCharacters(unittest.TestCase):
    def test_happy_path(self):
        secret = natwest.Natwest.natwest_secret(_ID, _PIN,
                                                _PASSWORD1, _PASSWORD2)

        pin_digits = ['Enter the 4th number',
                      'Enter the 2nd number',
                      'Enter the 3rd number']
        password_chars = ['Enter the 5th character',
                          'Enter the 7th character',
                          'Enter the 10th character']

        n = natwest.Natwest()
        a, b = n._select_characters(secret, pin_digits, password_chars)
        self.assertEqual(a, _PIN[3] + _PIN[1] + _PIN[2])
        self.assertEqual(b, _PASSWORD1[4] + _PASSWORD1[6] + _PASSWORD1[9])


if __name__ == '__main__':
    unittest.main()
