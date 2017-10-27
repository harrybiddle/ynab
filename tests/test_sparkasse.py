import unittest
import cStringIO

from ynab import sparkasse_de as sparkasse

class TestCommaFloat(unittest.TestCase):
    def test_float_to_string_conversion(self):
        self.assertEqual(sparkasse.comma_float_to_string(1.1), '1,1')
        self.assertEqual(sparkasse.comma_float_to_string(1000.1), '1000,1')

    def test_string_to_float_conversion(self):
        self.assertEqual(sparkasse.comma_string_to_float('1,1'), 1.1)
        self.assertEqual(sparkasse.comma_string_to_float('10'), 10)
        self.assertEqual(sparkasse.comma_string_to_float('-1,1'), -1.1)

    def test_exception_when_casting_word_to_float(self):
        with self.assertRaises(ValueError):
            sparkasse.comma_string_to_float('foo')

    def test_exception_when_casting_decimal_float_with_thousands_separator(self):
        with self.assertRaises(ValueError):
            sparkasse.comma_string_to_float('1,000.1')

class TestCSVConverstion(unittest.TestCase):
    valid_header = '"Order account";"Day of entry";"Value date";"Posting text";"Purpose";"Creditor ID";"Mandate reference";"Customer reference (End-to-End)";"Collective order reference";"Original direct debit amount";"Reimbursement of expenses for returning a direct debit";"Beneficiary/payer";"Account number / IBAN";"BIC (SWIFT code)";"Amount";"Currency";"Info"'
    valid_entry_format = '"1203059441";"26.10.17";"{date}";"ONLINE-UEBERWEISUNG";"{memo}";"";"";"";"";"";"";"{payee}";"GB79101111100264565115";"HGNKDEEFXYX";"{amount}";"EUR";"Transaction volume posted"'

    def valid_entry(self, date, payee, memo, amount):
        return self.valid_entry_format.format(date=date, payee=payee, memo=memo, amount=amount)

    def convert_csv(self, input_rows):
        input_string = '\n'.join(input_rows)
        input_stream = cStringIO.StringIO(input_string)
        output_stream = cStringIO.StringIO()
        sparkasse.convert_csv(input_stream, output_stream)
        lines = output_stream.getvalue().split('\n')
        stripped_lines = [l.strip('\r') for l in lines]
        non_empty_lines = [l for l in stripped_lines if l]
        return non_empty_lines

    def test_conversion(self):
        a = [self.valid_header,
             self.valid_entry('26.10.17', 'Mary Smith', 'DATUM 25.10.2017, 22.31 UHR, 1.TAN 999929 ', 13.49),
             self.valid_entry('25.10.17', 'John Smith', 'bitsnbobs', 150.0)]
        result = self.convert_csv(a)

        expected = ['Date,Payee,Category,Memo,Outflow,Inflow',
                    '10/26/2017,Mary Smith,,"DATUM 25.10.2017, 22.31 UHR, 1.TAN 999929 ","0,0","13,49"',
                    '10/25/2017,John Smith,,bitsnbobs,"0,0","150,0"']
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()