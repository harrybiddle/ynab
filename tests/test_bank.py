
import unittest

from ynab import bank


class TestUUIDs(unittest.TestCase):
    def test_construction_with_uuid(self):
        b = bank.Bank()
        self.assertTrue(len(b.uuid()) > 0)

    def test_uuids_unique(self):
        banks = [bank.Bank() for i in range(100)]
        uuids = [b.uuid() for b in banks]
        self.assertEqual(len(uuids), len(set(uuids)))

    def test_uuid_doesnt_change(self):
        b = bank.Bank()
        self.assertEqual(b.uuid(), b.uuid())

    def test_equality(self):
        a = bank.Bank()
        b = bank.Bank()
        self.assertEqual(a, a)
        self.assertNotEqual(a, b)

    def test_hash_equality(self):
        a = bank.Bank()
        b = bank.Bank()
        self.assertEqual(hash(a), hash(a))
        self.assertNotEqual(hash(a), hash(b))


class TestSecrets(unittest.TestCase):
    def setUp(self):
        secrets = {'password': 'pass123', 'pin': 1234}
        self.bank = bank.Bank(secrets)

    def test_validate_secrets_success(self):
        self.bank.validate_secrets('password', 'pin')

    def test_validate_unrecognised_secret_fails(self):
        with self.assertRaises(AssertionError):
            self.bank.validate_secrets('password', 'foo')

    def test_validate_too_few_secrets_fails(self):
        with self.assertRaises(AssertionError):
            self.bank.validate_secrets('password')

    def test_secret_lookup_success(self):
        self.assertEqual('pass123', self.bank.secret('password'))
        self.assertEqual(1234, self.bank.secret('pin'))

    def test_secret_lookup_failure(self):
        with self.assertRaises(KeyError):
            self.bank.secret('foo')


if __name__ == '__main__':
    unittest.main()
