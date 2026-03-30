import re


def detect_language(text: str) -> str:
    """Detect language from text. Returns 'uz', 'ru', or 'en'."""
    cyrillic = len(re.findall(r"[а-яёА-ЯЁ]", text))
    russian_markers = len(re.findall(r"[ыъёЫЪЁ]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))

    if cyrillic == 0 and latin > 0:
        return "en"
    if cyrillic > 0 and russian_markers > 0:
        return "ru"
    if cyrillic > 0:
        return "uz"
    return "en"
