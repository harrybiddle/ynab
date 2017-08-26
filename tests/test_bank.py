
import unittest

from ynab import bank

class TestBankUUIDs(unittest.TestCase):

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

class TestBankSecrets(unittest.TestCase):

    def test_secret_registration(self):
        b = bank.Bank(['password'])
        secrets = {b.uuid(): {'password': 'mypass'}}
        b.extract_secrets(secrets)
        self.assertEqual('mypass', b.secret('password'))

    def test_objects_with_two_uuids(self):
        b = bank.Bank(['password'])
        c = bank.Bank(['password'])
        secrets = {b.uuid(): {'password': 'mypass_b'},
                   c.uuid(): {'password': 'mypass_c'}}
        b.extract_secrets(secrets)
        c.extract_secrets(secrets)
        self.assertEqual('mypass_b', b.secret('password'))
        self.assertEqual('mypass_c', c.secret('password'))

    def test_error_on_non_existent_secret(self):
        b = bank.Bank(['password'])
        with self.assertRaises(KeyError):
            b.secret('foo')

    def test_default_secret_is_none(self):
        b = bank.Bank(['password'])
        self.assertEqual(None, b.secret('password'))

    def test_secret_names(self):
        s = ['foo', 'bar']
        b = bank.Bank(s)
        self.assertEqual(s, b.secret_names())

if __name__ == '__main__':
    unittest.main()
