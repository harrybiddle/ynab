import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as conditions

_WAIT_TIME_FOR_SUCCESSFUL_UPLOAD_SECONDS = 10


def _go_to_website(driver):
    driver.get('https://app.youneedabudget.com/')    

def _log_in(secret, driver):
    driver.find_element_by_xpath('//input[@placeholder="email address"]') \
          .send_keys(secret.ynab_email)

    driver.find_element_by_xpath('//input[@placeholder="password"]') \
          .send_keys(secret.ynab_password)

    driver.find_element_by_xpath('//button[text()="Sign In"]') \
          .click()


def _navigate_to_upload_screen(bank, driver):
    driver.find_element_by_xpath('//span[text()="' + bank.full_name + '"]') \
          .click()

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

    driver.find_element_by_xpath('//button[text()="OK"]').click()


def upload_transactions(bank, driver, paths):
    _go_to_website(driver)
    _log_in(bank.secret, driver)
    for path in paths:
        time.sleep(1)
        _navigate_to_upload_screen(bank, driver)
        time.sleep(1)
        _initiate_upload(driver, path)
        time.sleep(1)
        _wait_until_upload_confirmed_successful(driver)
