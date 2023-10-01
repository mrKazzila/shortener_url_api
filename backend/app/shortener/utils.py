import secrets
from string import ascii_lowercase, ascii_uppercase, digits


def create_secret_key(key: str) -> str:
    """
    Create a secret key from the given key and a random string.

    Args:
        key (str): The base key.

    Returns:
        str: The secret key.
    """
    if any([key is None, key == '']):
        raise ValueError('Key is None or empty!')

    return f"{key}_{generate_random_key(length=8)}"


def generate_random_key(length: int = 5) -> str:
    """
    Generate a random key of the given length.

    Args:
        length (int, optional): The length of the key. Defaults to 5.

    Returns:
        str: The random key.
    """
    if length <= 0:
        raise ValueError('length mast be more then 0')

    chars = ascii_lowercase + ascii_uppercase + digits
    return ''.join(secrets.choice(chars) for _ in range(length))