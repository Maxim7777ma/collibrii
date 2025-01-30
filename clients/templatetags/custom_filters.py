import json
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Получает значение из словаря по ключу.
    Если dictionary — это JSON-строка, декодирует её в словарь.
    """
    if isinstance(dictionary, str):
        try:
            dictionary = json.loads(dictionary)
        except json.JSONDecodeError:
            return None
    return dictionary.get(key, "-")  # Возвращает значение по ключу или "-", если ключа нет