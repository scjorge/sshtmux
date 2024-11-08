import json
import os

from cryptography.fernet import Fernet, InvalidToken

from sshtmux.core.config import settings
from sshtmux.exceptions import IdentityException


class KeyManager:
    def __init__(self):
        self.key_file = settings.sshtmux.SSHTMUX_IDENTITY_FILE
        self.key_env = settings.sshtmux.SSHTMUX_IDENTITY_KEY
        if self.key_env and isinstance(self.key_env, str) and len(self.key_env) > 0:
            self.key = self.key_env
        else:
            self.key = self._load_or_generate_key()

    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    def _load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = KeyManager.generate_key()
            self._save_key(key)
            return key

    def _save_key(self, key):
        with open(self.key_file, "wb") as f:
            f.write(key)

    def get_key(self):
        return self.key


class PasswordManager:
    def __init__(self, service):
        self.service = service
        self.key_manager = KeyManager()
        self.password_file = settings.sshtmux.SSHTMUX_IDENTITY_PASSWORDS_FILE
        self.fernet = Fernet(self.key_manager.get_key())

    def _encrypt_data(self, data):
        try:
            return self.fernet.encrypt(data.encode())
        except Exception as e:
            raise IdentityException(str(e))

    def _decrypt_data(self, encrypted_data):
        try:
            return self.fernet.decrypt(encrypted_data).decode()
        except Exception as e:
            raise IdentityException(str(e))

    def _load_identities(self):
        if not os.path.exists(self.password_file):
            return {}
        with open(self.password_file, "rb") as f:
            encrypted_data = f.read()
        return json.loads(self._decrypt_data(encrypted_data))

    def _save_identities(self, passwords):
        encrypted_data = self._encrypt_data(json.dumps(passwords))
        with open(self.password_file, "wb") as f:
            f.write(encrypted_data)

    def set_password(self, username, password):
        try:
            identities = self._load_identities()
        except InvalidToken:
            raise IdentityException("Invalid Token")
        except Exception as e:
            raise IdentityException(str(e))

        if not identities.get(self.service):
            identities[self.service] = {}
        identities[self.service][username] = password

        self._save_identities(identities)

    def get_password(self, username):
        identities = self._load_identities()
        users = identities.get(self.service)
        if not users:
            raise IdentityException("No Identities was Found")
        identity = users.get(username)
        if not identity:
            raise IdentityException("Identity not Found")
        return identity

    def delete_password(self, username):
        identities = self._load_identities()
        if not identities.get(self.service):
            return

        if username in identities[self.service]:
            del identities[self.service][username]
            self._save_identities(identities)
        else:
            raise IdentityException("User not Found")

    def get_identities(self):
        identities = self._load_identities()
        users = identities.get(self.service)
        return users.keys()
