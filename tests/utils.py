from __future__ import absolute_import, print_function, unicode_literals
import os


def not_live():
    return any([
        os.environ.get('KMS_ACCESS_KEY_ID') is None,
        os.environ.get('KMS_SECRET_ACCESS_KEY') is None,
        os.environ.get('KMS_ALIAS') is None,
    ])
