"""Keyboard layout mappings."""
from .hebrew import HEBREW_TO_EN, EN_TO_HEBREW
from .russian import RUSSIAN_TO_EN, EN_TO_RUSSIAN
from .arabic import ARABIC_TO_EN, EN_TO_ARABIC

# All available layouts: name → (foreign_to_en, en_to_foreign, unicode_range)
LAYOUTS = {
    'hebrew': {
        'to_en': HEBREW_TO_EN,
        'from_en': EN_TO_HEBREW,
        'range': ('\u0590', '\u05FF'),
        'label': 'Hebrew',
    },
    'russian': {
        'to_en': RUSSIAN_TO_EN,
        'from_en': EN_TO_RUSSIAN,
        'range': ('\u0400', '\u04FF'),
        'label': 'Russian',
    },
    'arabic': {
        'to_en': ARABIC_TO_EN,
        'from_en': EN_TO_ARABIC,
        'range': ('\u0600', '\u06FF'),
        'label': 'Arabic',
    },
}
