import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class AESCipher:
    def __init__(self, key: bytes):
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, data: bytes) -> bytes:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded = padder.update(data) + padder.finalize()
        return iv + encryptor.update(padded) + encryptor.finalize()

    @staticmethod
    def decrypt(key: bytes, data: bytes) -> bytes:
        key = hashlib.sha256(key).digest()
        iv, ct = data[:16], data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded = decryptor.update(ct) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()
