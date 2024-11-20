from base64 import b64encode, b64decode

from cryptography.fernet import Fernet
from django.conf import settings

CAP_MQTT_SECRET_KEY = getattr(settings, "CAP_MQTT_SECRET_KEY", None)


def encrypt_password(raw_password) -> str:
    """Encrypts the entered password and stores it in the
    encrypted_password field, in this way the password stored
    in the database is not in plain text.

    Args:
        raw_password (str): The raw password string entered
        by the user.

    Returns:
        str: The encrypted password string.
    """
    # Encrypts to a byte string
    cipher = Fernet(CAP_MQTT_SECRET_KEY)
    encrypted_password = cipher.encrypt(raw_password.encode())
    # Converts to a base64 string
    return b64encode(encrypted_password).decode()


def decrypt_password(encrypted_password) -> str:
    """Decrypts the stored broker password
    and returns the original entered password.

    Args:
        encrypted_password (str): The stored encrypted password

    Returns:
        str: The original password string entered by the user.
    """
    # Decrypt it using the Fernet key
    cipher = Fernet(CAP_MQTT_SECRET_KEY)
    encrypted_password = b64decode(encrypted_password.encode())
    return cipher.decrypt(encrypted_password).decode()
