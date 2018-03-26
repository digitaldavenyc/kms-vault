from __future__ import absolute_import, print_function, unicode_literals

import os

try:
    import mock
except ImportError:  # pragma: no cover
    from unittest import mock

from unittest import skipIf, TestCase
from kms_vault import Vault
from .utils import not_live


class VaultTests(TestCase):

    fixtures_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'fixtures'
    )

    def setUp(self):
        self.vault = Vault(os.path.join(self.fixtures_path, 'secrets.yml'))

    def test_instantiation(self):
        fake_path = '/path/to/secrets.yml'
        vault = Vault(fake_path)
        self.assertEqual(vault.secrets_file, fake_path)
        self.assertEqual(vault.secrets, {})

    def test_secrets_not_empty(self):
        self.assertNotEqual(self.vault.secrets, {})

    def test_get_success_via_decrypt(self):
        with mock.patch.object(self.vault, '_decrypt') as _decrypt:
            decypted = self.vault.get('staging.api_key')
            _decrypt.assert_called_once_with('fakekey')
            self.assertEqual(decypted, _decrypt('fakekey'))

    def test_get_success_via_envvar(self):
        os.environ.setdefault('API_KEY', 'secret')
        with mock.patch.object(self.vault, '_decrypt') as _decrypt:
            decypted = self.vault.get('staging.api_key')
            self.assertEqual(decypted, 'secret')
            self.assertEqual(_decrypt.call_count, 0)

    def test_add(self):
        self.vault.add('foo.bar.baz', 'bar')
        self.assertEqual(
            self.vault.secrets['foo']['bar']['baz'],
            'bar'
        )

    def test_decrypt_raises_on_invalid_path(self):
        self.assertRaises(ValueError, self.vault.decrypt, 'foo')

    @skipIf(not_live(), 'Not configured for integration tests.')
    def test_encrypt_and_decrypt_values(self):
        self.vault.key_alias = os.environ.get('KMS_ALIAS')
        secrets = {
            'foo': 'secret',
            'thing': 'test',
            'bar': {
                'key': 'secret'
            }
        }
        encrypted = self.vault.encrypt_values(secrets)
        self.assertNotEqual(secrets, encrypted)
        self.assertEqual(encrypted.keys(), secrets.keys())
        decrypted = self.vault.decrypt_values(encrypted)
        self.assertEqual(secrets, decrypted)

    def test_save(self):
        secrets_file = os.path.join(self.fixtures_path, 'secrets.enc')
        self.assertFalse(os.path.exists(secrets_file))
        vault = Vault(secrets_file)
        vault._secrets = {
            'foo': 'bar',
            'baz': {
                'test': {
                    'key': 'secret'
                }
            }
        }
        with mock.patch.object(vault, '_encrypt', return_value=1) as _encrypt:
            vault.save()
            self.assertTrue(_encrypt.called)
        self.assertTrue(os.path.exists(secrets_file))
        os.remove(secrets_file)
