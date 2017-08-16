import unittest
import os.path

from ynab.halifax_com import Halifax
import filecmp

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_TEST_FILE = os.path.join(_SCRIPT_DIR, 'test.qif')

class TestFileInverter(unittest.TestCase):
    def test_single_entry_invert(self):
        halifax = Halifax()
        inverted_file = halifax._invert_files([_TEST_FILE])
        self.assertTrue(filecmp.cmp(_TEST_FILE, inverted_file[0], shallow=False))

if __name__ == '__main__':
    unittest.main()
