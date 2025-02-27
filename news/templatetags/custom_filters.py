from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# Список нецензурных слов (можно расширить)
CENSORED_WORDS = ['редиска', 'bad', 'devil']

@register.filter(name='censor')
@stringfilter  # Гарантирует, что фильтр применяется только к строкам
def censor(value):
    if not isinstance(value, str):
        raise ValueError("Фильтр 'censor' применяется только к строкам.")

    for word in CENSORED_WORDS:
        # Заменяем слово на звёздочки
        value = value.replace(word, word[0] + '*' * (len(word) - 1))
        value = value.replace(word.capitalize(), word[0].capitalize() + '*' * (len(word) - 1))
    return value