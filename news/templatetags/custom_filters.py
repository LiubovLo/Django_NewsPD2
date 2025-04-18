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
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)

        # Заменяем все буквы кроме первой и последней на "*"
        def replace_chars(match):
            return match.group(1) + '*' * (len(match.group(2)) - 1) + match.group(3)

        text = pattern.sub(replace_chars, text)

    return text

@register.filter
def censor(text):
    if not isinstance(text, str):
        raise ValueError("The censor filter can only be applied to strings.")

    # Список нежелательных слов
    forbidden_words = ['редиска']  #  слова для цензора

    # Заменяем символы в нежелательных словах
    for word in forbidden_words:
        # Игнорируем регистр при поиске слова
        pattern = re.compile(r'(?<![^\W\d])' + re.escape(word) + r'(?![^\W\d])', re.IGNORECASE)
        # Заменяем все буквы кроме первой и последней на "*"
        def replace_chars(match):
            return match.group(0)[0] + '*' * (len(match.group(0)) - 2) + match.group(0)[-1]
        text = pattern.sub(replace_chars, text)

    return text