from collections import OrderedDict
from datetime import datetime
import csv
import os.path
import math

from bank import Bank
import fileutils


class SparkasseHeidelberg(Bank):
    ''' TODO:
     - Handle the case where there is already a .CSV file in the downloads
       directory
     - Switch to writing OFX files as these are better-supported by YNAB
     - Make the start date of the download configurable (and set in config!):
       at the moment we use the website default
    '''

    full_name = 'SparkasseHeidelberg'

    def __init__(self, config, secrets):
        super(SparkasseHeidelberg, self).__init__(secrets)
        self.validate_secrets('pin')
        self.username = config['username']

    def unique(self, list, failure_msg='Multiple elements found'):
        ''' Asserts that there is one item in the list and returns it
        '''
        assert len(list) == 1, failure_msg
        return list[0]

    def download_transactions(self, driver, dir):
        # TODO check that no CSV file exists before downloading it
        self.login(driver)
        self.assert_there_is_only_one_account(driver)
        self.navigate_to_transactions_table(driver)
        self.initiate_download(driver)
        return self.locate_csv_and_transform_to_ynab_format(dir)

    def login(self, driver):
        driver.get('https://www.sparkasse-heidelberg.de/en/home.html')

        x = '//label[starts-with(text(),"Login name")]'
        login_label = self.unique(driver.find_elements_by_xpath(x),
                                  failure_msg='Cannot locate login textbox')
        login_id = login_label.get_attribute('for')

        login = self.unique(driver.find_elements_by_id(login_id))
        login.send_keys(self.username)

        x = '//input[@type="password"]'
        pin = self.unique(driver.find_elements_by_xpath(x))

        pin.send_keys(self.secret('pin'))

        x = '//input[@type="submit"]'
        submit = self.unique(driver.find_elements_by_xpath(x))
        submit.click()

    def assert_there_is_only_one_account(self, driver):
        # check there is only one table on the page
        x = '//table[contains(@class, "table_widget_finanzstatus")]'
        self.unique(driver.find_elements_by_xpath(x))

        # count the rows in the table
        x = '//table[contains(@class, "table_widget_finanzstatus")]/tbody/tr'
        rows = len(driver.find_elements_by_xpath(x))
        assert rows == 4, ('Too many rows in finance status table. Do you '
                           'have more than one account? This script only '
                           'supports one account')

    def navigate_to_transactions_table(self, driver):
        x = '//input[@title="Transaction search"]'
        transactions = self.unique(driver.find_elements_by_xpath(x))
        transactions.click()

    def initiate_download(self, driver):
        x = '//span[@title="Export"]'
        export = self.unique(driver.find_elements_by_xpath(x))
        export.click()

        x = '//input[@value="CSV-CAMT-Format"]'
        csv_camt = self.unique(driver.find_elements_by_xpath(x))
        csv_camt.click()

    def locate_csv_and_transform_to_ynab_format(self, dir):
        csv_file = self.unique(fileutils.wait_for_file(dir, '.CSV'),
                               failure_msg=('Found multiple CSV files - '
                                            'expected only one'))

        output_csv_file = '-ynab_friendly'.join(os.path.splitext(csv_file))

        converter = CsvCamtToYnabFormat()
        converter.convert_csv_file(csv_file, output_csv_file)
        return output_csv_file


class CsvCamtToYnabFormat(object):
    ''' Converts the CSV-CAMT format to one that is supported by
    YouNeedABudget.com
    '''

    CAMT_SCHEMA = OrderedDict()
    CAMT_SCHEMA['Order account'] = 0
    CAMT_SCHEMA['Day of entry'] = 1
    CAMT_SCHEMA['Value date'] = 2
    CAMT_SCHEMA['Posting text'] = 3
    CAMT_SCHEMA['Purpose'] = 4
    CAMT_SCHEMA['Creditor ID'] = 5
    CAMT_SCHEMA['Mandate reference'] = 6
    CAMT_SCHEMA['Customer reference (End-to-End)'] = 7
    CAMT_SCHEMA['Collective order reference'] = 8
    CAMT_SCHEMA['Original direct debit amount'] = 9
    CAMT_SCHEMA['Reimbursement of expenses for returning a direct debit'] = 10
    CAMT_SCHEMA['Beneficiary/payer'] = 11
    CAMT_SCHEMA['Account number / IBAN'] = 12
    CAMT_SCHEMA['BIC (SWIFT code)'] = 13
    CAMT_SCHEMA['Amount'] = 14
    CAMT_SCHEMA['Currency'] = 15
    CAMT_SCHEMA['Info'] = 16

    DEFAULY_YNAB_DATE_FORMAT = '%m/%d/%Y'

    def comma_string_to_float(self, s):
        return float(s.replace(',', '.'))

    def comma_float_to_string(self, f):
        return str(f).replace('.', ',')

    def convert_csv(self, input_stream, output_stream):
        # check the CSV header is as expected
        input_csv = csv.reader(input_stream, delimiter=';')
        header = input_csv.next()
        cleaned_header = [h.strip('"') for h in header]
        assert (cleaned_header == self.CAMT_SCHEMA.keys())

        # write new output header
        output_csv = csv.writer(output_stream)
        output_csv.writerow(['Date', 'Payee', 'Category',
                             'Memo', 'Outflow', 'Inflow'])

        # transform each row of the input stream and write it
        for row in input_csv:
            # extract values
            date_string = row[self.CAMT_SCHEMA['Value date']]
            payee = row[self.CAMT_SCHEMA['Beneficiary/payer']]
            category = ''
            memo = row[self.CAMT_SCHEMA['Purpose']]
            amount_string = row[self.CAMT_SCHEMA['Amount']]

            # skip if there is an empty date - this is a transaction
            # that has not yet gone through
            if date_string == '':
                continue

            # parse values
            amount = self.comma_string_to_float(amount_string)
            inflow = max(0.0, amount)
            outflow = math.fabs(min(0.0, amount))
            date = datetime.strptime(date_string, '%d.%m.%y')

            # format to string
            inflow_string = self.comma_float_to_string(inflow)
            outflow_string = self.comma_float_to_string(outflow)
            new_date_string = date.strftime(self.DEFAULY_YNAB_DATE_FORMAT)

            # write values
            output_csv.writerow([new_date_string, payee, category, memo,
                                 outflow_string, inflow_string])

    def convert_csv_file(self, input_filename, output_filename):
        with open(input_filename, 'r') as i:
            with open(output_filename, 'w') as o:
                self.convert_csv(i, o)


if __name__ == '__main__':
    import sys
    input_filename, output_filename = sys.argv[1:3]
    CsvCamtToYnabFormat().convert_csv_file(input_filename, output_filename)
