from __future__ import absolute_import, print_function

import os
from unittest import TestCase
from click.testing import CliRunner
from kms_vault.scripts.kms_vault import cli


class TestKMSCommands(TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_click_scripts_functionality(self):
        result = self.runner.invoke(
            cli,
            [
                'encrypt',
                './tests/fixtures/secrets.yml',
                '--key-alias', 'kms-vault'
            ]
        )
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(
            cli,
            [
                'decrypt',
                './tests/fixtures/secrets.yml.enc',
            ]
        )
        self.assertEqual(result.exit_code, 0)

        os.remove('./tests/fixtures/secrets.yml.enc')
