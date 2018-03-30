
import unittest

from ete import EndToEndTestBase

_USERNAME = 'username'
_PASSWORD = 'pass1234'


class EndToEndTest(EndToEndTestBase, unittest.TestCase):
    ''' Runs the entire script through end to end, mocking out selenium, user
    input, and a bit of the file system '''
    def source_configuration(self):
        return {
            'type': 'amex',
            'username': _USERNAME,
            'secrets_keys': {
                'password': _PASSWORD
            }
        }

    def mock_chrome_driver(self, chrome_driver):
        chrome_driver.return_value.title = 'American Express'

    test_ete = EndToEndTestBase.ete


if __name__ == '__main__':
    unittest.main()
