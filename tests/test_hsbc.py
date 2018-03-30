import unittest

from ete import EndToEndTestBase

_USERNAME = 'username'
_MEMORABLE_QUESTION = 'linguine'
_SECURITY_CODE = '1234'


class EndToEndTest(EndToEndTestBase, unittest.TestCase):
    ''' Runs the entire script through end to end, mocking out selenium, user
    input, and a bit of the file system '''
    def source_configuration(self):
        return {
            'type': 'hsbc',
            'username': _USERNAME,
            'secrets_keys': {
                'memorable_question': _MEMORABLE_QUESTION,
                'security_code': _SECURITY_CODE
            }
        }

    def mock_chrome_driver(self, chrome_driver):
        ''' Provides return values for calls to driver.find_element_by_id that
        require a response for ynab.py to complete '''
        chrome_driver.return_value.title = 'HSBC'

    test_ete = EndToEndTestBase.ete


if __name__ == '__main__':
    unittest.main()
