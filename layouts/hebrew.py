"""Hebrew ↔ English keyboard layout mapping (standard Israeli QWERTY)."""

EN_TO_HEBREW = {
    # Lowercase
    'q': '/',  'w': '\'', 'e': 'ק',  'r': 'ר',  't': 'א',
    'y': 'ט',  'u': 'ו',  'i': 'ן',  'o': 'ם',  'p': 'פ',
    'a': 'ש',  's': 'ד',  'd': 'ג',  'f': 'כ',  'g': 'ע',
    'h': 'י',  'j': 'ח',  'k': 'ל',  'l': 'ך',
    'z': 'ז',  'x': 'ס',  'c': 'ב',  'v': 'ה',  'b': 'נ',
    'n': 'מ',  'm': 'צ',
    # Punctuation
    ',': 'ת',  '.': 'ץ',  '/': '.',
    ';': 'ף',  '\'': ',',
    '[': ']',  ']': '[',
    # Shifted
    'Q': '/',  'W': '\'', 'E': 'ק',  'R': 'ר',  'T': 'א',
    'Y': 'ט',  'U': 'ו',  'I': 'ן',  'O': 'ם',  'P': 'פ',
    'A': 'ש',  'S': 'ד',  'D': 'ג',  'F': 'כ',  'G': 'ע',
    'H': 'י',  'J': 'ח',  'K': 'ל',  'L': 'ך',
    'Z': 'ז',  'X': 'ס',  'C': 'ב',  'V': 'ה',  'B': 'נ',
    'N': 'מ',  'M': 'צ',
    '<': 'ת',  '>': 'ץ',  '?': '.',
    ':': 'ף',  '"': ',',
}

# Build reverse mapping, preferring lowercase English keys
HEBREW_TO_EN = {}
for k, v in EN_TO_HEBREW.items():
    if v not in HEBREW_TO_EN or k.islower() or not k.isalpha():
        HEBREW_TO_EN[v] = k
