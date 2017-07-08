"""Run PEP8 on all Python files from the repository root. Modified from
https://gist.github.com/swenson/8142788 """

import os
import os.path
import unittest

import pep8

_REPOSITORY_ROOT = os.path.join(os.path.dirname(__file__), '..')


class TestPep8(unittest.TestCase):
    """Run PEP8 on all files from the repository root."""
    def test_pep8(self):
        style = pep8.StyleGuide()
        errors = 0
        for root, _, files in os.walk(_REPOSITORY_ROOT):
            python_filenames = [f for f in files if f.endswith('.py')]
            python_files = [os.path.join(root, f) for f in python_filenames]
            errors = style.check_files(python_files).total_errors
        self.assertEqual(errors, 0)
