"""Run PEP8 on all Python files from the repository root. Modified from
https://gist.github.com/swenson/8142788 """

import os
import unittest

import pep8

_REPOSITORY_ROOT = os.path.join(os.path.dirname(__file__), '..')


def recursive_file_match(dir, predicate):
    """Walks DIR recursively and yields the file path of any
    file F where predicate(F) is truthy."""
    for root, dirs, files in os.walk(dir):
        for file in files:
            if predicate(file):
                yield os.path.join(root, file)


class TestPep8(unittest.TestCase):
    """Run PEP8 on all files from the repository root."""
    def test_pep8(self):
        style = pep8.StyleGuide()
        python_files = recursive_file_match(_REPOSITORY_ROOT,
                                            lambda f: f.endswith('.py'))
        result = style.check_files(python_files)
        self.assertEqual(result.total_errors, 0)
