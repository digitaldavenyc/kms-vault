from __future__ import absolute_import, print_function, unicode_literals

from unittest import TestCase
from kms_vault.utils import walk


class TestUtils(TestCase):

    def test_walk_raises_on_incorrect_type(self):
        self.assertRaises(TypeError, walk, [], lambda x: x)
