YNAB
====

Selenium automation to download transactions from online banking websites
then upload them to YouNeedABudget.com.

To run tests:

	pip install --user -r requirements.txt
	python tests/test.py

To install locally:

    python setup.py bdist_wheel
    pip install dist/ynab*.whl
