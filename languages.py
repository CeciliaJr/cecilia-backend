def detect_language(text):
    t = text.lower()

    # espanhol
    if any(c in t for c in ["á", "é", "í", "ó", "ú", "ñ"]) or "hola" in t:
        return "es"

    # inglês
    if any(w in t for w in ["hello", "hi", "ok", "thanks"]):
        return "en"

    return "pt"
