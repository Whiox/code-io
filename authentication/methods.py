"""Методы, необходимые для аунтефикации"""

import random
import string
from user_agents import parse


def generate_password():
    """Генерирует случайный пароль формата XXXX-XXXX-XXXX"""
    parts = ["".join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)]
    return "-".join(parts)


def get_client_ip(request):
    """Возвращает IP-адрес пользователя"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent_info(request):
    """Возвращает информацию о браузере и ОС пользователя"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed_ua = parse(user_agent)

    return {
        "browser": parsed_ua.browser.family,  # Chrome, Firefox, etc.
        "browser_version": parsed_ua.browser.version_string,  # Версия браузера
        "os": parsed_ua.os.family,  # Windows, MacOS, Linux, etc.
        "os_version": parsed_ua.os.version_string,  # Версия ОС
        "device": parsed_ua.device.family,  # iPhone, Samsung, etc.
    }


def user_info_view(request):
    """Группирует информацию о пользователе"""
    ip = get_client_ip(request)
    user_info = get_user_agent_info(request)

    return {
        "ip": ip,
        "browser": user_info["browser"],
        "browser_version": user_info["browser_version"],
        "os": user_info["os"],
        "os_version": user_info["os_version"],
        "device": user_info["device"],
    }


def is_author(request, reset_request):
    """Проверяет, совпадают ли данные пользователя с последним запросом на сброс пароля."""
    if not reset_request:
        return False

    info = get_user_agent_info(request)
    ip = get_client_ip(request)

    return (
        reset_request.ip == ip and
        reset_request.browser == info["browser"] and
        reset_request.browser_version == info["browser_version"] and
        reset_request.os == info["os"] and
        reset_request.os_version == info["os_version"] and
        reset_request.device == info["device"]
    )
