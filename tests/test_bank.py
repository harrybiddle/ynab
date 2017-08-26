
import unittest

from ynab import bank

class TestBank(unittest.TestCase):
    def test_construction_with_uuid(self):
        b = bank.Bank()
        b.generate_uuid()
        self.assertTrue(len(b.uuid()) > 0)

if __name__ == '__main__':
    unittest.main()
