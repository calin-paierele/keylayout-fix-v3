"""Arabic ↔ English keyboard layout mapping (standard Arabic QWERTY)."""

EN_TO_ARABIC = {
    # Lowercase
    'q': 'ض',  'w': 'ص',  'e': 'ث',  'r': 'ق',  't': 'ف',
    'y': 'غ',  'u': 'ع',  'i': 'ه',  'o': 'خ',  'p': 'ح',
    '[': 'ج',  ']': 'د',
    'a': 'ش',  's': 'س',  'd': 'ي',  'f': 'ب',  'g': 'ل',
    'h': 'ا',  'j': 'ت',  'k': 'ن',  'l': 'م',
    ';': 'ك',  '\'': 'ط',
    'z': 'ئ',  'x': 'ء',  'c': 'ؤ',  'v': 'ر',  'b': 'لا',
    'n': 'ى',  'm': 'ة',
    ',': 'و',  '.': 'ز',  '/': 'ظ',
    '`': 'ذ',
    # Shifted
    'Q': 'َ',   'W': 'ً',   'E': 'ُ',   'R': 'ٌ',   'T': 'لإ',
    'Y': 'إ',  'U': '\'', 'I': '÷',  'O': '×',  'P': '؛',
    '{': '<',  '}': '>',
    'A': 'ِ',   'S': 'ٍ',   'D': ']',  'F': '[',  'G': 'لأ',
    'H': 'أ',  'J': 'ـ',  'K': '،',  'L': '/',
    ':': ':',  '"': '"',
    'Z': '~',  'X': 'ْ',   'C': '}',  'V': '{',  'B': 'لآ',
    'N': 'آ',  'M': '\'',
    '<': ',',  '>': '.',  '?': '؟',
    '~': 'ّ',
}

# Build reverse mapping, preferring lowercase English keys
ARABIC_TO_EN = {}
for k, v in EN_TO_ARABIC.items():
    if v not in ARABIC_TO_EN or k.islower() or not k.isalpha():
        ARABIC_TO_EN[v] = k
