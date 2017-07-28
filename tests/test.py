import os
import sys
import unittest
import commentjson

from ynab import ynab

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
        wm.WebsiteDefinition([{'page_id': 'foo', 'start': True,
                               'elements': [{'href': 'bar'}]},
                              {'page_id': 'bar',
                               'elements': [{'href': 'baz'}]},
                              {'page_id': 'baz'}])

    def test_start_page_extracted(self):
        page = {'page_id': 'foo', 'start': True, 'key': 'value'}
        d = wm.WebsiteDefinition([page])
        self.assertEqual('foo', d.start_page)
        self.assertEqual(page, d.get_page('foo'))

    def test_raise_key_error_when_no_elements(self):
        page = {}
        with self.assertRaises(KeyError):
            wm.WebsiteDefinition.find_element_in_page(page, 'name', 'foo')

    def test_raise_key_error_when_no_elements_matching(self):
        page = {'elements': [{}]}
        with self.assertRaises(KeyError):
            wm.WebsiteDefinition.find_element_in_page(page, 'name', 'foo')

    def test_return_element(self):
        element = {'name': 'foo', 'key': 'value'}
        page = {'elements': [element]}
        found_element = wm.WebsiteDefinition.find_element_in_page(page, 'name', 'foo')
        self.assertEqual(element, found_element)


class TestWebsiteMock(unittest.TestCase):
    def test_current_page_is_starting_page(self):
        w = wm.WebsiteMock.fromjson([{'page_id': 'foo', 'start': True},
                                     {'page_id': 'bar'}])
        self.assertEqual('foo', w.current_page())

    def test_find_element_by_name(self):
        element = {'name': 'button', 'key': 'value'}
        w = wm.WebsiteMock.fromjson([{'page_id': 'foo', 'start': True,
                                      'elements': [element]}])
        found_element = w.find_element_by_name('button')
        self.assertEqual(element, found_element.contents)

    def test_find_element_by_id(self):
        element = {'id': 'button', 'key': 'value'}
        w = wm.WebsiteMock.fromjson([{'page_id': 'foo', 'start': True,
                                      'elements': [element]}])
        found_element = w.find_element_by_id('button')
        self.assertEqual(element, found_element.contents)

    def test_find_element_by_xpath(self):
        xpath = '\\*[text()="Statements"]'
        element = {'xpath': xpath, 'key': 'value'}
        w = wm.WebsiteMock.fromjson([{'page_id': 'foo', 'start': True,
                                      'elements': [element]}])
        found_element = w.find_element_by_xpath(xpath)
        self.assertEqual(element, found_element.contents)

    def test_clicking_on_element_changes_current_page(self):
        w = wm.WebsiteMock.fromjson([{'page_id': 'foo', 'start': True,
                                      'elements': [{'name': 'button', 'href': 'bar'}]},
                                     {'page_id': 'bar'}])
        el = w.find_element_by_name('button')
        el.click()
        self.assertEqual('bar', w.current_page())


class TestElement(unittest.TestCase):
    def test_element_text_is_none_if_no_test(self):
        el = wm.Element(None, {})
        self.assertEqual(None, el.text)

    def test_element_text_extracted(self):
        el = wm.Element(None, {'text': 'foo'})
        self.assertEqual('foo', el.text)

    def test_send_keys(self):
        element = {}
        el = wm.Element(None, element)
        el.send_keys('foo')
        self.assertEqual('foo', element['input'])


if __name__ == '__main__':
    unittest.main()
