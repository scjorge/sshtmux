import json
import os

from cryptography.fernet import Fernet, InvalidToken
from rich.console import Console
from rich.prompt import Prompt

from sshtmux.core.config import settings
from sshtmux.exceptions import IdentityException


class KeyManager:
    def __init__(self):
        self.key_file = settings.sshtmux.SSHTMUX_IDENTITY_KEY_FILE
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
    def __init__(self, service=settings.internal_config.BASE_SERVICE):
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

    def set_password(self, reference, password, is_update=False):
        try:
            identities = self._load_identities()
        except InvalidToken:
            raise IdentityException("Invalid Token")
        except Exception as e:
            raise IdentityException(str(e))

        if not identities.get(self.service):
            identities[self.service] = {}
        identity = identities[self.service].get(reference)

        if not is_update:
            if identity:
                raise IdentityException("Identity already exists")
        identities[self.service][reference] = password

        self._save_identities(identities)

    def get_password(self, reference):
        identities = self._load_identities()
        users = identities.get(self.service)
        if not users:
            raise IdentityException("No Identities was Found")
        identity = users.get(reference)
        if not identity:
            raise IdentityException("Identity not Found")
        return identity

    def delete_password(self, reference):
        identities = self._load_identities()
        if not identities.get(self.service):
            return

        if reference in identities[self.service]:
            del identities[self.service][reference]
            self._save_identities(identities)
        else:
            raise IdentityException("User not Found")

    def get_identities(self):
        identities = self._load_identities()
        users = identities.get(self.service)
        if not users:
            return []
        return list(users.keys())


def prompt_identity():
    console = Console()
    password_manager = PasswordManager()
    identities = ["Cancel"] + password_manager.get_identities()
    identities_idx = [str(index) for index, _ in enumerate(identities)]

    console.print("Identities:", style="bold underline")
    for idx, option in enumerate(identities):
        console.print(f"{idx}. {option}")

    choice = Prompt.ask(
        "Choose Identity:",
        choices=identities_idx,
        default=identities_idx[0],
        show_choices=False,
    )
    identity = identities[int(choice)]
    if identity == identities[0]:
        return

    password = password_manager.get_password(identity)
    return password
