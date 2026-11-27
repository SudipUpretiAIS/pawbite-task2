import os

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import TypeDecorator, Text


class DataEncryptionError(Exception):
    pass


def get_cipher():
    key = os.getenv("DATA_ENCRYPTION_KEY")

    if not key:
        raise DataEncryptionError(
            "Encryption key is not configured."
        )

    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, TypeError):
        raise DataEncryptionError(
            "Invalid encryption key."
        ) from None


def encrypt_data(value):
    if value is None:
        return None

    return get_cipher().encrypt(
        value.encode("utf-8")
    ).decode("ascii")


def decrypt_data(value):
    if value is None:
        return None

    try:
        return get_cipher().decrypt(
            value.encode("ascii")
        ).decode("utf-8")

    except (InvalidToken, UnicodeError):
        raise DataEncryptionError(
            "Unable to decrypt protected data."
        ) from None


class EncryptedString(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return encrypt_data(value)

    def process_result_value(self, value, dialect):
        return decrypt_data(value)