import unittest

from ynab import natwest_com as natwest

_ID = '1234768965'
_PIN = '9750'
_PASSWORD = 'mycrazyp!asswithatleasttencharacters'

class TestSelectCharacters(unittest.TestCase):

    def test_happy_path(self):
        pin_digits = ['Enter the 4th number',
                      'Enter the 2nd number',
                      'Enter the 3rd number']
        password_chars = ['Enter the 5th character',
                          'Enter the 7th character',
                          'Enter the 10th character']

        n = natwest.Natwest(None)
        n.extract_secrets({'customer id': _ID,
                           'pin': _PIN,
                           'password': _PASSWORD})

        a, b = n._select_characters(pin_digits, password_chars)
        self.assertEqual(a, _PIN[3] + _PIN[1] + _PIN[2])
        self.assertEqual(b, _PASSWORD[4] + _PASSWORD[6] + _PASSWORD[9])


if __name__ == '__main__':
    unittest.main()
