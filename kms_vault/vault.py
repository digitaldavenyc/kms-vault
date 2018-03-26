from __future__ import absolute_import, print_function, unicode_literals
import base64
import os
import yaml
import boto3
import pydash
from copy import deepcopy
try:
    from functools import lru_cache
except ImportError:  # pragma: no cover
    from functools32 import lru_cache

from .utils import get_section, walk


class Vault(object):
    """Use a Vault instance to access secrets encrypted using amazons kms service.

    Usage:
        # path/to/secrets/encrypted.yml
        staging:
            google_api_secret: ...encrypted...
            stripe_api_secret: ...encrypted...

        production:
            google_api_secret: ...encrypted...
            stripe_api_secret: ...encrypted...


        vault = Vault('path/to/secrets/encrypted.yml')
        value = vault.get('staging.google_api_secret')
        # value should be the decrypted version of path/to/secrets/encrypted.yml

        # if you want to override the use of that value locally for testing add
        # an environment variable `GOOGLE_API_SECRET=supersecretvalue`.

        value = vault.get('staging.google_api_secret')
        # value == 'supersecretvalue'
    """

    def __init__(
        self,
        secrets_file,
        key_alias=None,
        prefix=None,
        profile=None,
        encryption_context=None
    ):
        self.secrets_file = secrets_file
        self.prefix = prefix or ''
        self.key_alias = key_alias
        self._secrets = None
        self._kms = None
        self.profile = profile
        self.encryption_context = encryption_context or {'vault': 'secrets'}

    @property
    def kms(self):
        """Instantiate the boto kms client."""
        if self._kms is None:
            session = boto3.Session(
                aws_access_key_id=os.getenv('KMS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('KMS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('KMS_REGION_NAME', 'us-east-1'),
                profile_name=self.profile
            )
            self._kms = session.client('kms')
        return self._kms

    def decrypt_values(self, obj):
        # find all of the values and decrypt them, replace the original value
        obj_copy = deepcopy(obj)
        walk(obj_copy, self._decrypt)
        return obj_copy

    def decrypt(self, path):
        """Decrypt the value reference by path in the secrets file using kms."""
        enc_value = pydash.get(self.secrets, path)
        if not enc_value:
            raise ValueError('Specified path does not exist.')
        return self._decrypt(enc_value)

    def _decrypt(self, value):
        response = self.kms.decrypt(
            CiphertextBlob=base64.b64decode(value),
            EncryptionContext=self.encryption_context
        )
        return response['Plaintext'].decode('utf-8')

    def encrypt_values(self, obj):
        # find all of the values and encrypt them, replace the original value
        obj_copy = deepcopy(obj)
        walk(obj_copy, self._encrypt)
        return obj_copy

    def _encrypt(self, value):
        response = self.kms.encrypt(
            KeyId='alias/' + self.key_alias,
            Plaintext=value,
            EncryptionContext=self.encryption_context
        )
        return base64.b64encode(response['CiphertextBlob']).decode('utf-8')

    def load_secrets(self):
        if os.path.exists(self.secrets_file):
            with open(self.secrets_file, 'r') as secrets_file:
                secrets = yaml.safe_load(secrets_file)
        else:
            secrets = {}
        return secrets

    @property
    def secrets(self):
        """Load and cache the contents of the encrypted secrets file."""
        if self._secrets is None:
            self._secrets = self.load_secrets()
        return self._secrets

    @lru_cache()
    def get(self, path):
        """Return the value associated to the givent path.

        First check the local environment variables for a matching pattern,
        else try the encrypted file.
        """
        name = path.rsplit('.', 1)[-1].upper()
        return os.getenv(self.prefix + name) or self.decrypt(path)

    def add(self, path, value, delimiter=None):
        delimiter = delimiter or '.'
        keys = path.split(delimiter)
        section = get_section(self.secrets, keys[:-1])
        section[keys[-1]] = value

    def save(self):
        encrypted = self.encrypt_values(self.secrets)
        with open(self.secrets_file, 'w') as output_file:
            yaml.safe_dump(encrypted, output_file, default_flow_style=False)
