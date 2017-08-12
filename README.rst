YNAB
====

Selenium automation to download transactions from online banking websites
then upload them to YouNeedABudget.com.

Usage:

	ynab my_configuration.yml

For example configuration, see the `tests/ynab.conf` example file.

To run tests:

	python setup.py test

To install locally:

    python setup.py bdist_wheel
    pip install dist/ynab*.whl


