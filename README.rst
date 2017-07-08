YNAB
====

Selenium automation to download transactions from online banking websites
then upload them to YouNeedABudget.com.

To run tests:

	python setup.py test

To install locally:

    python setup.py bdist_wheel
    pip install dist/ynab*.whl
