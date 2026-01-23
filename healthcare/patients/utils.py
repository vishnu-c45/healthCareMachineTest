from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.FERNET_SECRET_KEY)


def encrypt_value(value: str) -> str:
    if value is None:
        return None
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    if value is None:
        return None
    return fernet.decrypt(value.encode()).decode()
