#!/usr/bin/env python
from __future__ import absolute_import, print_function

import os
import click
import yaml
from kms_vault import Vault


@click.group()
def cli():
    pass


@click.command()
@click.argument('file_input', type=click.Path(exists=True))
@click.option('--key-alias', default=None, type=click.STRING)
@click.option('--profile', default=None, type=click.STRING)
@click.option('--out', default=None, type=click.Path(writable=True))
def encrypt(file_input, key_alias, profile, out):
    vault = Vault(file_input, key_alias=key_alias, profile=profile)
    output = vault.encrypt_values(vault.secrets)
    if out is None:
        out = file_input + '.enc'

    with open(out, 'w') as file_output:
        yaml.safe_dump(
            output,
            file_output,
            default_flow_style=False,
            encoding='utf-8'
        )


@click.command()
@click.argument('file_input', type=click.Path(exists=True))
@click.option('--profile', default=None, type=click.STRING)
@click.option('--out', default=None, type=click.Path(writable=True))
def decrypt(file_input, profile, out):
    vault = Vault(file_input, profile=profile)
    output = vault.decrypt_values(vault.secrets)
    if out is None:
        out = os.path.join(
            os.path.dirname(os.path.abspath(file_input)),
            os.path.basename(file_input).replace('.enc', '')
        )

    with open(out, 'w') as file_output:
        yaml.safe_dump(
            output,
            file_output,
            default_flow_style=False,
            encoding='utf-8'
        )


cli.add_command(encrypt)
cli.add_command(decrypt)
