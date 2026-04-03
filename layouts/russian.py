"""Russian ↔ English keyboard layout mapping (standard ЙЦУКЕН)."""

EN_TO_RUSSIAN = {
    # Lowercase
    'q': 'й',  'w': 'ц',  'e': 'у',  'r': 'к',  't': 'е',
    'y': 'н',  'u': 'г',  'i': 'ш',  'o': 'щ',  'p': 'з',
    '[': 'х',  ']': 'ъ',
    'a': 'ф',  's': 'ы',  'd': 'в',  'f': 'а',  'g': 'п',
    'h': 'р',  'j': 'о',  'k': 'л',  'l': 'д',
    ';': 'ж',  '\'': 'э',
    'z': 'я',  'x': 'ч',  'c': 'с',  'v': 'м',  'b': 'и',
    'n': 'т',  'm': 'ь',
    ',': 'б',  '.': 'ю',  '/': '.',
    '`': 'ё',
    # Uppercase
    'Q': 'Й',  'W': 'Ц',  'E': 'У',  'R': 'К',  'T': 'Е',
    'Y': 'Н',  'U': 'Г',  'I': 'Ш',  'O': 'Щ',  'P': 'З',
    '{': 'Х',  '}': 'Ъ',
    'A': 'Ф',  'S': 'Ы',  'D': 'В',  'F': 'А',  'G': 'П',
    'H': 'Р',  'J': 'О',  'K': 'Л',  'L': 'Д',
    ':': 'Ж',  '"': 'Э',
    'Z': 'Я',  'X': 'Ч',  'C': 'С',  'V': 'М',  'B': 'И',
    'N': 'Т',  'M': 'Ь',
    '<': 'Б',  '>': 'Ю',
    '~': 'Ё',
}

# Build reverse mapping, preferring lowercase English keys
RUSSIAN_TO_EN = {}
for k, v in EN_TO_RUSSIAN.items():
    if v not in RUSSIAN_TO_EN or k.islower() or not k.isalpha():
        RUSSIAN_TO_EN[v] = k
