import unittest
import website_mock as wm


def page_json(id, start=False, elements=None):
    ''' Constructs a JSON blob that represents a mocked website page '''
    ret = {'page_id': id}
    if start:
        ret['start'] = True
    if elements is not None:
        ret['elements'] = elements
    return ret


class TestWebsiteDefinition(unittest.TestCase):
    wd = wm.WebsiteDefinition

    def test_empty_schema_raises(self):
        with self.assertRaises(wm.SchemaException):
            self.wd([])

    def test_fails_when_more_than_one_start_page(self):
        with self.assertRaises(wm.SchemaException):
            self.wd([page_json('foo1', True),
                     page_json('foo2', True)])

    def test_fails_when_page_ids_not_unique(self):
        with self.assertRaises(wm.SchemaException):
            self.wd([page_json('foo', True),
                     page_json('foo')])

    def test_fails_when_element_points_to_non_existant_page(self):
        elements = [{'href': 'non-existing'}]
        with self.assertRaises(wm.SchemaException):
            self.wd([page_json('foo', True, elements)])

    def test_suceeds_when_element_points_to_existing_page(self):
        elements = [{'href': 'bar'}]
        self.wd([page_json('foo', True, elements),
                 page_json('bar')])

    def test_fails_when_second_element_points_to_non_existant_page(self):
        foo_elements = [{'href': 'bar'}]
        bar_elements = [{'href': 'baz'}]
        with self.assertRaises(wm.SchemaException):
            self.wd([page_json('foo', True, foo_elements),
                     page_json('bar', elements=bar_elements)])

    def test_suceeds_when_second_element_points_to_existing_page(self):
        foo_elements = [{'href': 'bar'}]
        bar_elements = [{'href': 'baz'}]
        self.wd([page_json('foo', True, foo_elements),
                 page_json('bar', elements=bar_elements),
                 page_json('baz')])

    def test_start_page_extracted(self):
        page = page_json('foo', True)
        d = self.wd([page])
        self.assertEqual('foo', d.start_page)
        self.assertEqual(page, d.get_page('foo'))

    def test_raise_key_error_when_no_elements(self):
        page = {}
        with self.assertRaises(KeyError):
            self.wd.find_element_in_page(page, 'name', 'foo')

    def test_raise_key_error_when_no_elements_matching(self):
        page = {'elements': [{}]}
        with self.assertRaises(KeyError):
            self.wd.find_element_in_page(page, 'name', 'foo')

    def test_return_element(self):
        element = {'name': 'foo', 'key': 'value'}
        page = {'elements': [element]}
        found_element = self.wd.find_element_in_page(page, 'name', 'foo')
        self.assertEqual(element, found_element)


class TestDriver(unittest.TestCase):
    def test_current_page_is_starting_page(self):
        w = wm.Driver.fromjson([page_json('foo', True),
                                page_json('bar')])
        self.assertEqual('foo', w.current_page())

    def test_find_element_by_name(self):
        element = {'name': 'button', 'key': 'value'}
        w = wm.Driver.fromjson([page_json('foo', True, [element])])
        found_element = w.find_element_by_name('button')
        self.assertEqual(element, found_element.contents)

    def test_find_element_by_id(self):
        element = {'id': 'button', 'key': 'value'}
        w = wm.Driver.fromjson([page_json('foo', True, [element])])
        found_element = w.find_element_by_id('button')
        self.assertEqual(element, found_element.contents)

    def test_find_element_by_xpath(self):
        xpath = '\\*[text()="Statements"]'
        element = {'xpath': xpath, 'key': 'value'}
        w = wm.Driver.fromjson([page_json('foo', True, [element])])
        found_element = w.find_element_by_xpath(xpath)
        self.assertEqual(element, found_element.contents)

    def test_clicking_on_element_changes_current_page(self):
        elements = [{'name': 'button', 'href': 'bar'}]
        w = wm.Driver.fromjson([page_json('foo', True, elements),
                                page_json('bar')])
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
