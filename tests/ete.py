import tempfile

import yaml
from mock import MagicMock, patch

from ynab import ynab


class EndToEndTestBase(object):

    def setUp(self):
        # TODO reset this afterwards
        ynab.TEMPORARY_DIRECTORY = tempfile.gettempdir()

    # these functions are intended to be defined by the derived class
    def source_configuration(self):
        ''' Should return the configuration of the bank, e.g.
        {'type': 'natwest', 'customer_number': ...} '''
        return {}

    def mock_chrome_driver(self, chrome_driver):
        pass

    def mock_action_chains(self, action_chains):
        pass

    def mock_select(self, select):
        pass

    def mock_clickable(self, clickable):
        clickable.return_value(lambda x: x)

    def mock_get_password(self, get_password):
        get_password.return_value = 'password'

    def mock_glob(self, glob):
        glob.return_value = 'foo'

    # some convenience methods for mocking selenium methods
    def mock_driver_method(self, chrome_driver, driver_method, responses):
        ''' Can be used to define the value of calls like

                driver.find_element_by_id(arg).text

            Args:
                chrome_driver: the chrome_driver mock object
                responses: a dict of arg -> responses, for example
                    {'id_of_page_title': 'Natwest'}
                driver_method: the method to mock, for example
                    'find_element_by_id'
        '''
        def mock_function(arg):
            r = MagicMock()
            if arg in responses:
                r.text = responses[arg]
            return r

        # set 'mock_function' as a side effect of chrome_driver.driver_method
        fn = getattr(chrome_driver.return_value, driver_method, None)
        fn.side_effect = mock_function

    # this is the test method: derived class should rename this
    # 'test_<somthing>'
    @patch('glob.glob')
    @patch('keyring.get_password')
    @patch('selenium.webdriver.support.expected_conditions.element_to_be_clickable')  # noqa
    @patch('selenium.webdriver.support.ui.Select')
    @patch('selenium.webdriver.ActionChains')
    @patch('selenium.webdriver.Chrome')
    def ete(self, chrome_driver, action_chains, select, clickable,
            get_password, glob):
        # provide opportunity to configure mocks
        self.mock_chrome_driver(chrome_driver)
        self.mock_action_chains(action_chains)
        self.mock_select(select)
        self.mock_clickable(clickable)
        self.mock_get_password(get_password)
        self.mock_glob(glob)

        # serialise configuration to file and run the script
        with tempfile.NamedTemporaryFile() as serialised_configuration:
            yaml.dump(self._configuration(), serialised_configuration)
            self.assertEquals(0, ynab.main([serialised_configuration.name]))

    def _configuration(self):
        config = {
            'ynab': {
                'email': 'email@domain.com',
                'secrets_keys': {
                    'password': 'password'
                },
                'targets': [{
                    'budget': 'My Budget',
                    'account': 'My Account'
                }]
            },
            'keyring': {
                'username': 'johnsnow'
            }
        }
        config['sources'] = [self.source_configuration()]
        return config
