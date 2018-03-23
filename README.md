# kms-vault

A simple pip installable library for encrypting secrets using the AWS key management service.

## Installation

`pip install kms-vault`

## Usage

* Log into AWS console.
* Create a new IAM user. Or if you already have one make sure to create an access key for that user.
* Stay in the IAM console and on the left there should be a link to `Encryption Keys`.
* Once in the Encryption Keys section create a new key, make note fo the `Alias` you use.
* Add the IAM user as an administrator on the encryption key.
