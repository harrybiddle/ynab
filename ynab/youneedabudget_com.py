import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as conditions

_WAIT_TIME_AFTER_EACH_CLICK_SECONDS = 10
_WAIT_TIME_FOR_SUCCESSFUL_UPLOAD_SECONDS = 10


def _go_to_website(driver):
    driver.get('https://app.youneedabudget.com/')


def _log_in(secret, driver, email):
    driver.find_element_by_xpath('//input[@placeholder="email address"]') \
          .send_keys(email)

    driver.find_element_by_xpath('//input[@placeholder="password"]') \
          .send_keys(secret.ynab_password)

    driver.find_element_by_xpath('//button[text()="Sign In"]') \
          .click()


def _navigate_to_upload_screen(driver, budget, account):
    # choose budget dropdown
    budget_dropdown = '//button[contains(@class,"button-prefs-budget")]'
    driver.find_element_by_xpath(budget_dropdown) \
          .click()

    # navigate to the list of budgets
    open_budget = '//*[text()="Open a budget"]'
    driver.find_element_by_xpath(open_budget) \
          .click()

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
    driver.find_element_by_xpath('//span[text()="{}"]'.format(account)) \
          .click()

    # click the import transactions button
    x = '//*[contains(@class,"accounts-toolbar-file-import-transactions")]'
    driver.find_element_by_xpath(x) \
          .click()


def _initiate_upload(driver, path):
    driver.find_element_by_xpath('//input[@type="file"]') \
          .send_keys(os.path.expanduser(path))

    x = '//button[text()="Import" and contains(@class,"button-primary")]'
    driver.find_element_by_xpath(x) \
          .click()


def _wait_until_upload_confirmed_successful(driver):
    wait = WebDriverWait(driver, _WAIT_TIME_FOR_SUCCESSFUL_UPLOAD_SECONDS)
    success_div = (By.XPATH, '//div[text()="Import Successful"]')
    wait.until(conditions.presence_of_element_located(success_div))


def upload_transactions(secret, driver, path, config, email):
    driver.implicitly_wait(_WAIT_TIME_AFTER_EACH_CLICK_SECONDS)
    _go_to_website(driver)
    _log_in(secret, driver, email)
    _navigate_to_upload_screen(driver, config['budget'], config['account'])
    _initiate_upload(driver, path)
    _wait_until_upload_confirmed_successful(driver)
