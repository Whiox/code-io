import random
import string

def generate_password():
    """Генерирует случайный пароль формата XXXX-XXXX-XXXX"""
    parts = ["".join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)]
    return "-".join(parts)