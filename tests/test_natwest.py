import unittest
import tempfile

from mock import MagicMock
from mock import patch
import yaml

from ynab import natwest_com as natwest
from ynab import ynab

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

class EndToEndTest(unittest.TestCase):
    ''' Runs the entire script through end to end, mocking out selenium, user
    input, and a bit of the file system '''
    configuration = {
            'sources': [{
                'type': 'natwest',
                'customer_number': '12345678',
                'secrets_keys': {
                    'password': 'password',
                    'pin': 'pin'
                }
            }],
            'ynab': {
                'email': 'email@domain.com',
                'secrets_keys': {
                    'password': 'password'
                },
                'targets': [{
                    'budget': 'My Budget',
                    'account': 'My Account'
                }]
            },
            'keyring': {
                'username': 'johnsnow'
            }
        }

    def setUp(self):
        ynab.TEMPORARY_DIRECTORY = tempfile.gettempdir()

    def mock_necessary_website_responses(self, chrome_driver_mock):
        ''' Provides return values for calls to driver.find_element_by_id that
        require a response for ynab.py to complete '''
        def mock_function(arg):
            args_that_require_response = {
                natwest.PIN_DIGIT_1: '1',
                natwest.PIN_DIGIT_2: '2',
                natwest.PIN_DIGIT_3: '3',
                natwest.PASSWORD_CHARACTER_1: '4',
                natwest.PASSWORD_CHARACTER_2: '5',
                natwest.PASSWORD_CHARACTER_3: '6'
            }
            r = MagicMock()
            if arg in args_that_require_response:
                r.text = args_that_require_response[arg]
            return r

        chrome_driver_mock.return_value.find_element_by_id.side_effect = \
            mock_function

    @patch('glob.glob', return_value=['file.ofx'])
    @patch('keyring.get_password', return_value='password')
    @patch('selenium.webdriver.support.ui.Select')
    @patch('selenium.webdriver.Chrome')
    def test_ete(self, chrome_driver, *unused):
        self.mock_necessary_website_responses(chrome_driver)
        with tempfile.NamedTemporaryFile() as serialised_configuration:
            yaml.dump(self.configuration, serialised_configuration)
            self.assertEquals(0, ynab.main([serialised_configuration.name]))


if __name__ == '__main__':
    unittest.main()
