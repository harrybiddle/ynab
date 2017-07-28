''' This module is intended to mock out Selenium: it replaces a real
webpage through Chrome with a mocked JSON model, so that you can test code that
uses Selenium without requiring Chrome.

You define a JSON model and pass it to the Driver class. The Driver class
behaves like Selenium's webdriver classes (albeit with very little
functionality!). The JSON model consists of a list of 'pages', each which can
have multiple 'elements'. The Driver stores the state of which page is the
current page, and any element state.

Here is an example of how a JSON mode would look:

    {
      "page_id": "first_page",
      "elements": [
        {"name": "my_link", "href": "second_page"}
      ]
    },
      {
        "page_id": "second_page"
      },
     ...

Exactly one page should contain the key 'start', which designates that it
is the first page to be loaded. If any element has a 'href' it is 'clickable',
and clicking on that page will update the Driver's current page to the target.
All hrefs must point to pages that exist. A page does not need to contain
elements, and there are no restrictions placed on the keys that an element has.
'''

import commentjson

# Keys that are used in the schema for a WebsiteModel

_START_PAGE_KEY = 'start'
_PAGE_ID_KEY = 'page_id'
_ELEMENTS_KEY = 'elements'
_HREF_KEY = 'href'
_NAME_KEY = 'name'
_ID_KEY = 'id'
_XPATH_KEY = 'xpath'
_TEXT_KEY = 'text'


class SchemaException(Exception):
    def __init__(self, cause):
        msg = 'Failed to parse schema, caused by ' + repr(cause)
        super(SchemaException, self).__init__(msg)
        self.cause = cause


class WebsiteModel():
    ''' Wraps the JSON model of the website, and parses it on construction,
    checking that the schema is correct, and that there aren't any hanging
    links '''

    def __init__(self, json_object):
        ''' Raises SchemaException if the JSON object does not conform to the
        required schema; if there are any hrefs to pages that don't exist; if
        there is not exactly one start page, or if there are any duplicate
        pages '''
        try:
            wd = WebsiteModel
            self.pages = wd._get_unique_pages(json_object)
            self.start_page = wd._get_unique_start_page_id(self.pages.values())
            wd._verify_hrefs_exist(self.pages, self.start_page)
        except Exception as e:
            raise SchemaException(e)

    def get_page(self, page_id):
        ''' Given a string page ID, Returns the full JSON object describing the
        page '''
        return self.pages[page_id]

    @staticmethod
    def find_element_in_page(page, key, identifier):
        ''' Given a JSON object for the page, tries to find an element that
        contains the given key/identifier pair.
        Raises: KeyError if there are no matching elements
        '''
        if _ELEMENTS_KEY in page:
            ret = []
            for element in page[_ELEMENTS_KEY]:
                if key in element and element[key] == identifier:
                    ret.append(element)
            if len(ret) == 0:
                raise KeyError(key + ': ' + identifier)
            return ret[0]
        else:
            raise KeyError('No elements in page')

    @staticmethod
    def _verify_hrefs_exist(pages, start_page_id):
        ''' Recurses through all pages and asserts that if any element has a href
        to another page id then that page id exists
        '''
        start_page = pages[start_page_id]
        if _ELEMENTS_KEY in start_page:
            for element in start_page[_ELEMENTS_KEY]:
                if _HREF_KEY in element:
                    target_id = element[_HREF_KEY]
                    targets = filter(lambda el: el[_PAGE_ID_KEY] == target_id,
                                     pages.values())
                    assert (len(targets) == 1)
                    WebsiteModel._verify_hrefs_exist(pages, target_id)

    @staticmethod
    def _get_unique_pages(js):
        ''' Get all valid pages from the JSON object: i.e. dicts that have a page ID
        Asserts that no two pages share the same page ID
        '''
        pages = [el for el in js if _PAGE_ID_KEY in el]
        pages_dict = dict([(el[_PAGE_ID_KEY], el) for el in pages])
        assert (len(pages) == len(pages_dict))
        return pages_dict

    @staticmethod
    def _get_unique_start_page_id(pages):
        ''' In a list of pages, find the starting page and return its page id.
        Asserts that there is exactly one starting page.
        '''
        start_pages = [el for el in pages if _START_PAGE_KEY in el]
        assert (len(start_pages) == 1)
        return start_pages[0][_PAGE_ID_KEY]


class Select():
    ''' A mock of selenium.webdriver.support.ui.Select. Currently does nothing
    whatsoever! '''
    def __init__(self, _):
        pass

    def select_by_visible_text(self, _):
        pass


class Element():
    ''' A page element, which can be clicked on, typed into, etc.
    The class stores a reference back to the Driver so that the 'browser' state
    can be updated following actions taken on the Element'''
    def __init__(self, website, element):
        self._website = website
        self.contents = element
        self.text = element[_TEXT_KEY] if _TEXT_KEY in element else None

    def click(self):
        if _HREF_KEY in self.contents:
            target_page_id = self.contents[_HREF_KEY]
            self._website.set_current_page(target_page_id)

    def send_keys(self, keys):
        self.contents['input'] = keys

    def submit(self):
        self.click()


class Driver():
    ''' A mock of selenium's webdriver classes '''
    @classmethod
    def fromfile(cls, json_filename):
        ''' Construct from a file path to a JSON file, comments allowed. See
        the module description for the expected schema of this JSON blob'''
        with open(json_filename) as file:
            js = commentjson.load(file)
            return cls.fromjson(js)

    @classmethod
    def fromjson(cls, json_object):
        ''' Construct from a JSON blob. See the module description for the
        expected schema of this JSON blob'''
        definition = WebsiteModel(json_object)
        return cls(definition)

    def __init__(self, definition):
        ''' Initialise from a WebsiteModel '''
        self.definition = definition
        start_page = self.definition.start_page
        self._current_page = self.definition.get_page(start_page)

    def set_current_page(self, new_page_id):
        self._current_page = self.definition.get_page(new_page_id)

    def current_page(self):
        return self._current_page[_PAGE_ID_KEY]

    def find_element_by_name(self, name):
        page = self._current_page
        e = WebsiteModel.find_element_in_page(page, _NAME_KEY, name)
        return Element(self, e)

    def find_element_by_xpath(self, xpath):
        page = self._current_page
        e = WebsiteModel.find_element_in_page(page, _XPATH_KEY, xpath)
        return Element(self, e)

    def find_element_by_id(self, id):
        page = self._current_page
        e = WebsiteModel.find_element_in_page(page, _ID_KEY, id)
        return Element(self, e)

    def get(self, _):
        pass

    def switch_to_default_content(self):
        pass

    def switch_to_frame(self, _):
        pass
