import sys
import csv
from collections import OrderedDict
import locale
from datetime import datetime
import math

SCHEMA = OrderedDict()
SCHEMA['Order account'] = 0
SCHEMA['Day of entry'] = 1
SCHEMA['Value date'] = 2
SCHEMA['Posting text'] = 3
SCHEMA['Purpose'] = 4
SCHEMA['Creditor ID'] = 5
SCHEMA['Mandate reference'] = 6
SCHEMA['Customer reference (End-to-End)'] = 7
SCHEMA['Collective order reference'] = 8
SCHEMA['Original direct debit amount'] = 9
SCHEMA['Reimbursement of expenses for returning a direct debit'] = 10
SCHEMA['Beneficiary/payer'] = 11
SCHEMA['Account number / IBAN'] = 12
SCHEMA['BIC (SWIFT code)'] = 13
SCHEMA['Amount'] = 14
SCHEMA['Currency'] = 15
SCHEMA['Info'] = 16

DEFAULY_YNAB_DATE_FORMAT = '%m/%d/%Y'

def comma_string_to_float(s):
    return float(s.replace(',', '.'))

def comma_float_to_string(f):
    return str(f).replace('.', ',')

def convert_csv(input_stream, output_stream):
    # check the CSV header is as expected
    input_csv = csv.reader(input_stream, delimiter=';')
    header = input_csv.next()
    cleaned_header = [h.strip('"') for h in header]
    assert (header == SCHEMA.keys())

    # write new output header
    output_csv = csv.writer(output_stream)
    output_csv.writerow(['Date','Payee','Category','Memo','Outflow','Inflow'])

    # transform each row of the input stream and write it
    for row in input_csv:
        # extract values
        date_string = row[SCHEMA['Value date']]
        payee = row[SCHEMA['Beneficiary/payer']]
        category = ''
        memo = row[SCHEMA['Purpose']]
        amount_string = row[SCHEMA['Amount']]

        # skip if there is an empty date - this is a transaction
        # that has not yet gone through
        if date_string == '':
            continue

        # parse values
        amount = comma_string_to_float(amount_string)
        inflow = max(0.0, amount)
        outflow = math.fabs(min(0.0, amount))
        date = datetime.strptime(date_string, '%d.%m.%y')

        # format to string
        inflow_string = comma_float_to_string(inflow)
        outflow_string = comma_float_to_string(outflow)
        new_date_string = date.strftime(DEFAULY_YNAB_DATE_FORMAT)

        # write values
        output_csv.writerow([new_date_string, payee, category, memo, outflow_string, inflow_string])

def main(argv):
    output_stream = sys.stdout
    with open(argv[0]) as input_stream:
        convert_csv(input_stream, output_stream)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
