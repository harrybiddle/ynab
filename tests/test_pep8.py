"""Run PEP8 on all Python files from the repository root. Modified from
https://gist.github.com/swenson/8142788 """

import os
import unittest

import pep8

_REPOSITORY_ROOT = os.path.join(os.path.dirname(__file__), '..')
_EXCLUDE_DIRS = ['build']


def get_all_python_files_in_repository():
    for root, dirs, files in os.walk(_REPOSITORY_ROOT):
        dirs[:] = [d for d in dirs if d not in _EXCLUDE_DIRS]
        for file in files:
            if file.endswith('.py'):
                yield os.path.join(root, file)


class TestPep8(unittest.TestCase):
    """Run PEP8 on all files from the repository root."""
    def test_pep8(self):
        if not 'YNAB_SKIP_PEP8_TEST' in os.environ:
            style = pep8.StyleGuide(ignore='E302')
            python_files = get_all_python_files_in_repository()
            result = style.check_files(python_files)
            self.assertEqual(result.total_errors, 0)
