
import unittest

from ynab import bank

class TestBank(unittest.TestCase):
    def test_construction_with_uuid(self):
        b = bank.Bank()
        b.generate_uuid()
        self.assertTrue(len(b.uuid()) > 0)

    def test_uuid_generation_fails_if_already_exists(self):
    	b = bank.Bank()
    	b.generate_uuid()
    	with self.assertRaises(Exception):
            b.generate_uuid()

if __name__ == '__main__':
    unittest.main()
