import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as conditions

from bank import Bank

_WAIT_TIME_FOR_SUCCESSFUL_UPLOAD_SECONDS = 10

class YNAB(Bank):

    full_name = 'YNAB'

    def __init__(self, config):
        super(YNAB, self).__init__(['password'])
        self.email = config['email']
        assert (len(config['targets']) == 1, 'Requires exactly one target')
        self.target_config = config['targets'][0]

    def upload_transactions(self, bank, driver, paths):
        self._go_to_website(driver)
        self._log_in(driver, self.email)
        for path in paths:
            time.sleep(1)
            self._navigate_to_upload_screen(driver,
                                            self.target_config['budget'],
                                            self.target_config['account'])
            time.sleep(1)
            self._initiate_upload(driver, path)
            time.sleep(1)
            self._wait_until_upload_confirmed_successful(driver)

    def _go_to_website(self, driver):
        driver.get('https://app.youneedabudget.com/')

    def _log_in(self, driver, email):
        driver.find_element_by_xpath('//input[@placeholder="email address"]') \
              .send_keys(email)

        driver.find_element_by_xpath('//input[@placeholder="password"]') \
              .send_keys(self.secret('password'))

        driver.find_element_by_xpath('//button[text()="Sign In"]') \
              .click()


    def _navigate_to_upload_screen(self, driver, budget, account):
        # choose budget dropdown
        budget_dropdown = '//button[contains(@class,"button-prefs-budget")]'
        driver.find_element_by_xpath(budget_dropdown).click()

        # navigate to the list of budgets
        open_budget = '//*[text()="Open Budget"]'
        driver.find_element_by_xpath(open_budget).click()

        # find our chosen budget text
        chosen_budget = ('//button[text()="{}"'
                         ' and contains(@class,"select-budget")]').format(budget)
        element = driver.find_element_by_xpath(chosen_budget)

        # get the URL for the budget from the parent and visit it
        # if we were just to click on the budget text, selenium complains
        # that another element would actually receive the click
        parent_element = element.find_element_by_xpath('..')
        url = parent_element.get_attribute('href')
        driver.get(url)

        # choosen the right account
        driver.find_element_by_xpath('//span[text()="{}"]'.format(account)).click()

        # click the import transactions button
        x = '//*[contains(@class,"accounts-toolbar-file-import-transactions")]'
        driver.find_element_by_xpath(x).click()


    def _initiate_upload(self, driver, path):
        driver.find_element_by_xpath('//input[@type="file"]') \
              .send_keys(os.path.expanduser(path))

        x = '//button[text()="Import" and contains(@class,"button-primary")]'
        driver.find_element_by_xpath(x) \
              .click()


    def _wait_until_upload_confirmed_successful(self, driver):
        wait = WebDriverWait(driver, _WAIT_TIME_FOR_SUCCESSFUL_UPLOAD_SECONDS)
        success_div = (By.XPATH, '//div[text()="Import Successful"]')
        wait.until(conditions.presence_of_element_located(success_div))

        driver.find_element_by_xpath('//button[text()="OK"]').click()
