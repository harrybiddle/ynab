import filecmp
import os.path
import unittest

from tests.ete import EndToEndTestBase
from ynab.halifax_com import CHALLENGE_DESCRIPTION_CLASS_NAME, Halifax

_USERNAME = "username"
_PASSWORD = "pass1234"
_CHALLENGE = "1234"
_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_TEST_FILE = os.path.join(_SCRIPT_DIR, "test.qif")
_TEST_RESULT_FILE = os.path.join(_SCRIPT_DIR, "test_correct.qif")


class TestFileInverter(unittest.TestCase):
    def test_single_entry_invert(self):
        halifax = Halifax({"username": None}, {"password": None, "challenge": None})
        inverted_file = halifax._invert_files([_TEST_FILE])
        self.assertTrue(filecmp.cmp(_TEST_RESULT_FILE, inverted_file[0], shallow=False))


class EndToEndTest(EndToEndTestBase, unittest.TestCase):
    """ Runs the entire script through end to end, mocking out selenium, user
    input, and a bit of the file system """

    def source_configuration(self):
        return {
            "type": "halifax",
            "username": _USERNAME,
            "secrets_keys": {"password": _PASSWORD, "challenge": _CHALLENGE},
        }

    def mock_chrome_driver(self, chrome_driver):
        """ Provides return values for calls to driver.find_element_by_id that
        require a response for ynab.py to complete """
        name = "Please enter characters 1, 2 and 3"
        responses = {CHALLENGE_DESCRIPTION_CLASS_NAME: name}
        self.mock_driver_method(chrome_driver, "find_element_by_class_name", responses)
        chrome_driver.return_value.title = "Halifax"

    def mock_glob(self, glob):
        glob.return_value = [_TEST_FILE]

    test_ete = EndToEndTestBase.ete


if __name__ == "__main__":
    unittest.main()
