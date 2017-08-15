import unittest

from ynab.halifax_com import Halifax
import filecmp

_TEST_FILE = 'test.qif'

class TestFileInverter(unittest.TestCase):
    def test_single_entry_invert(self):
        halifax = Halifax()
        inverted_file = halifax._invert_files([_TEST_FILE])
        self.assertTrue(filecmp.cmp(_TEST_FILE, inverted_file[0], shallow=False))

if __name__ == '__main__':
    unittest.main()
