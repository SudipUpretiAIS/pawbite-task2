import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet

from shop.encryption import (
    encrypt_data,
    decrypt_data,
    DataEncryptionError
)


class EncryptionTests(unittest.TestCase):

    def setUp(self):
        self.key = Fernet.generate_key().decode()

        self.env = patch.dict(
            "os.environ",
            {"DATA_ENCRYPTION_KEY": self.key}
        )

        self.env.start()
        self.addCleanup(self.env.stop)

        self.username = "Kalyan Sapkota"

    def test_encryption(self):
        encrypted = encrypt_data(self.username)
        self.assertNotEqual(encrypted, self.username)

    def test_decryption(self):
        encrypted = encrypt_data(self.username)
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, self.username)

    def test_random_ciphertext(self):
        first = encrypt_data(self.username)
        second = encrypt_data(self.username)
        self.assertNotEqual(first, second)

    def test_invalid_ciphertext(self):
        with self.assertRaises(DataEncryptionError):
            decrypt_data("invalid-ciphertext")

    def test_wrong_key(self):
        encrypted = encrypt_data(self.username)

        with patch.dict(
            "os.environ",
            {
                "DATA_ENCRYPTION_KEY":
                    Fernet.generate_key().decode()
            }
        ):
            with self.assertRaises(DataEncryptionError):
                decrypt_data(encrypted)

    def test_missing_key(self):
        with patch.dict(
            "os.environ",
            {"DATA_ENCRYPTION_KEY": ""}
        ):
            with self.assertRaises(DataEncryptionError):
                encrypt_data(self.username)


if __name__ == "__main__":
    unittest.main()