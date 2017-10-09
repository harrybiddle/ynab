import unittest

from ynab import natwest_com as natwest
from ete import EndToEndTestBase

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

        secrets = {'pin': _PIN, 'password': _PASSWORD}
        n = natwest.Natwest({'customer_number': _ID}, secrets)

        a, b = n._select_characters(pin_digits, password_chars)
        self.assertEqual(a, _PIN[3] + _PIN[1] + _PIN[2])
        self.assertEqual(b, _PASSWORD[4] + _PASSWORD[6] + _PASSWORD[9])

class EndToEndTest(EndToEndTestBase, unittest.TestCase):
    ''' Runs the entire script through end to end, mocking out selenium, user
    input, and a bit of the file system '''
    def source_configuration(self):
     return {
            'type': 'natwest',
            'customer_number': '12345678',
            'secrets_keys': {
                'password': 'password',
                'pin': 'pin'
            }
        }

    def mock_chrome_driver(self, chrome_driver):
        ''' Provides return values for calls to driver.find_element_by_id that
        require a response for ynab.py to complete '''
        responses = {
            natwest.PIN_DIGIT_1: '1',
            natwest.PIN_DIGIT_2: '2',
            natwest.PIN_DIGIT_3: '3',
            natwest.PASSWORD_CHARACTER_1: '4',
            natwest.PASSWORD_CHARACTER_2: '5',
            natwest.PASSWORD_CHARACTER_3: '6'
        }
        self.mock_driver_method(chrome_driver, 'find_element_by_id',
                                responses)

    test_ete = EndToEndTestBase.ete

if __name__ == '__main__':
    unittest.main()
