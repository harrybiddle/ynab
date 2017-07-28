import os
import sys
import unittest
import tempfile

from ynab import ynab
from ynab import natwest_com as natwest

import website_mock as wm

_ID = '1234768965'
_PIN = '9750'
_PASSWORD1 = 'mycrazyp!asswithatleasttencharacters'
_EMAIL = 'who@you.com'
_PASSWORD2 = 'myothercrazypas8s'


class TestSecret(unittest.TestCase):
    def test_valid_construction(self):
        secret_text = ';'.join([_ID, _PIN, _PASSWORD1, _EMAIL, _PASSWORD2])
        s = ynab.parse_secret(secret_text)
        self.assertEqual(s.customer_number, _ID)
        self.assertEqual(s.pin, _PIN)
        self.assertEqual(s.natwest_password, _PASSWORD1)
        self.assertEqual(s.email, _EMAIL)
        self.assertEqual(s.ynab_password, _PASSWORD2)


class TestSelectCharacters(unittest.TestCase):
    def test_happy_path(self):
        secret = ynab.Secret(_ID, _PIN, _PASSWORD1, _EMAIL, _PASSWORD2)

        pin_digits = ['Enter the 4th number',
                      'Enter the 2nd number',
                      'Enter the 3rd number']
        password_chars = ['Enter the 5th character',
                          'Enter the 7th character',
                          'Enter the 10th character']

        a, b = natwest._select_characters(secret, pin_digits, password_chars)
        self.assertEqual(a, _PIN[3] + _PIN[1] + _PIN[2])
        self.assertEqual(b, _PASSWORD1[4] + _PASSWORD1[6] + _PASSWORD1[9])

class TestWebsiteDefinition(unittest.TestCase):
    def test_empty_schema_raises(self):
        with self.assertRaises(wm.SchemaException):
            wm.WebsiteDefinition([])

    def test_fails_when_more_than_one_start_page(self):
        with self.assertRaises(wm.SchemaException):
            wm.WebsiteDefinition([{'page_id': 'foo1', 'start': True},
                                  {'page_id': 'foo2', 'start': True}])


    def test_fails_when_page_ids_not_unique(self):
        with self.assertRaises(wm.SchemaException):
            wm.WebsiteDefinition([{'page_id': 'foo', 'start': True},
                                                {'page_id': 'foo'}])

    def test_fails_when_element_points_to_non_existant_page(self):
        with self.assertRaises(wm.SchemaException):
            wm.WebsiteDefinition([{'page_id': 'foo', 'start': True,
                                   'elements': [{'href': 'non-existing'}]}])

    def test_suceeds_when_element_points_to_existing_page(self):
        with self.assertRaises(wm.SchemaException):
            wm.WebsiteDefinition([{'page_id': 'foo', 'start': True,
                                   'elements': [{'href': 'bar'}]},
                                   {'page_id': 'bar'}])

    def test_fails_when_second_element_points_to_non_existant_page(self):
        with self.assertRaises(wm.SchemaException):
            wm.WebsiteDefinition([{'page_id': 'foo', 'start': True,
                                   'elements': [{'href': 'bar'}]},
                                  {'page_id': 'bar',
                                   'elements': [{'href': 'baz'}]}])

    def test_suceeds_when_second_element_points_to_existing_page(self):
        with self.assertRaises(wm.SchemaException):
            wm.WebsiteDefinition([{'page_id': 'foo', 'start': True,
                                   'elements': [{'href': 'bar'}]},
                                  {'page_id': 'bar',
                                   'elements': [{'href': 'baz'}]},
                                  {'page_id': 'baz'}])

    def test_start_page_extracted(self):
        d = wm.WebsiteDefinition([{'page_id': 'foo', 'start': True}])
        self.assertEqual('foo', d.start_page)
if __name__ == '__main__':
    unittest.main()
