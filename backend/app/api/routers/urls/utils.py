import logging
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits

from app.settings.config import settings

__all__ = ("generate_random_key",)

logger = logging.getLogger(__name__)

LENGTH = settings().KEY_LENGTH
CHARS = f'{ascii_lowercase}{ascii_uppercase}{digits}'


def generate_random_key() -> str:
    """Generate a random key of the given length."""
    return "".join(choice(CHARS) for _ in range(LENGTH))
