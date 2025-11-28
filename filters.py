def sanitize_input(text):
    forbidden = [
        "matar", "morte", "arma", "sexo", "ódio", "política",
        "drogas", "adulto", "violento"
    ]
    for w in forbidden:
        text = text.replace(w, "")
    return text.strip()


def sanitize_output(text):
    forbidden = ["adulto", "violência", "sexo", "morte", "arma"]
    for w in forbidden:
        if w in text.lower():
            return "Desculpa Audrey 💜 Eu não sei falar sobre isso. Vamos brincar de outra coisa? ✨"
    return text
