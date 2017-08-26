
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

    def test_uuids_unique(self):
    	banks = [bank.Bank() for i in range(100)]
    	for b in banks:
    		b.generate_uuid()
        uuids = [b.uuid() for b in banks]
        self.assertEqual(len(uuids), len(set(uuids)))

if __name__ == '__main__':
    unittest.main()
