import filecmp
import os.path
import tempfile
import unittest

from mock import MagicMock, patch
import yaml

from ynab import ynab
from ynab.halifax_com import CHALLENGE_DESCRIPTION_CLASS_NAME
from ynab.halifax_com import Halifax

_USERNAME = 'username'
_PASSWORD = 'pass1234'
_CHALLENGE = '1234'
_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_TEST_FILE = os.path.join(_SCRIPT_DIR, 'test.qif')
_TEST_RESULT_FILE = os.path.join(_SCRIPT_DIR, 'test_correct.qif')

class TestFileInverter(unittest.TestCase):
    def test_single_entry_invert(self):
        halifax = Halifax({'username': None}, {'password': None, 'challenge': None})
        inverted_file = halifax._invert_files([_TEST_FILE])
        self.assertTrue(filecmp.cmp(_TEST_RESULT_FILE,
                                    inverted_file[0],
                                    shallow=False))

class EndToEndTest(unittest.TestCase):
    ''' Runs the entire script through end to end, mocking out selenium, user
    input, and a bit of the file system '''
    configuration = {
            'sources': [{
                'type': 'halifax',
                'username': _USERNAME,
                'secrets_keys': {
                    'password': _PASSWORD,
                    'challenge': _CHALLENGE
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
                CHALLENGE_DESCRIPTION_CLASS_NAME: 'Please enter characters 1, 2 and 3'
            }
            r = MagicMock()
            if arg in args_that_require_response:
                r.text = args_that_require_response[arg]
            return r

        chrome_driver_mock.return_value.find_element_by_class_name.side_effect = \
            mock_function
        chrome_driver_mock.return_value.title = 'Halifax'

    @patch('glob.glob', return_value=[_TEST_FILE])
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
