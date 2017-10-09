import unittest
import tempfile

from mock import patch
import yaml

from ynab import hsbc_com as hsbc
from ynab import ynab

_USERNAME = 'username'
_MEMORABLE_QUESTION = 'linguine'
_SECURITY_CODE = '1234'

class EndToEndTest(unittest.TestCase):
    ''' Runs the entire script through end to end, mocking out selenium, user
    input, and a bit of the file system '''
    configuration = {
            'sources': [{
                'type': 'hsbc',
                'username': _USERNAME,
                'secrets_keys': {
                    'memorable_question': _MEMORABLE_QUESTION,
                    'security_code': _SECURITY_CODE
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
        chrome_driver_mock.return_value.title = 'HSBC'

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
