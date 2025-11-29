from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

from filters import sanitize_input, sanitize_output
from languages import detect_language
from utils import load_persona

# ========================
#  Filtro de temas sensíveis
# ========================

BANNED_KEYWORDS = [
    # sexo / conteúdo adulto
    "sexo", "sexual", "porn", "pornografia", "porno", "nudez", "nua", "nu",
    "nudes", "nude", "orgasmo", "fetiche", "fetish",
    # drogas / abuso
    "maconha", "cocaína", "cocaina", "heroína", "heroina", "lsd",
    "ácido", "acido", "droga", "drogas", "cheirar pó", "cheirar cocaína",
    "bebida alcoólica", "bebida alcoolica", "ficar bêbado", "ficar bebado",
    # autoagressão / suicídio
    "suicídio", "suicidio", "me matar", "se matar", "tirar a própria vida",
    "tirar minha vida", "quero morrer", "não quero mais viver",
    "me cortar", "me cortar todo", "cortar os pulsos", "automutilação",
    "automutilacao", "me machucar de propósito", "me machucar de proposito",
    # violência pesada
    "tortura", "desmembrar", "esquartejar", "matar alguém", "matar alguem",
    "assassinar", "assassinato brutal", "matar pessoas por diversão",
]

def is_sensitive(text: str) -> bool:
    """Verifica se o texto contém palavras-chave sensíveis."""
    t = text.lower()
    return any(p in t for p in BANNED_KEYWORDS)


# ========================
#  Cliente OpenAI + App
# ========================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carrega a persona da Cecília a partir do arquivo de texto
persona = load_persona("persona_cecilia.txt")

# Cria a aplicação FastAPI
app = FastAPI()

# Configura CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois você pode restringir se quiser
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    message: str


@app.post("/cecilia")
async def talk_to_cecilia(msg: Message):
    """
    Endpoint principal: recebe uma mensagem da Audrey,
    passa pelos filtros e retorna a resposta da Cecília.
    """
    # Limpa o texto de entrada
    text = sanitize_input(msg.message)

    # 1) Filtro de temas sensíveis ANTES de chamar o modelo
    if is_sensitive(text):
        safe_reply = (
            "Desculpa, Audrey 💜. Esse é um assunto de adulto ou muito sério, "
            "e eu não posso falar sobre isso aqui. "
            "Se algo estiver te incomodando de verdade, por favor conversa com "
            "um adulto de confiança (papai, mamãe, responsável, família ou professora), tá bem? "
            "Eu posso brincar com você, contar histórias, te ajudar com a escola "
            "ou falar sobre espaço, animais, roblox e um monte de coisas legais! ✨"
        )
        return {"reply": safe_reply}

    # Detecta idioma básico (pt/es/en)
    lang = detect_language(text)

    # Monta texto do usuário
    user_text = f"Audrey disse ({lang}): {text}"

    # 2) Chama o modelo da OpenAI com a persona da Cecília
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": user_text},
            ],
            max_tokens=300,
            temperature=0.8,
        )

        reply = response.choices[0].message.content.strip()
        reply = sanitize_output(reply)

        return {"reply": reply}

    except Exception as e:
        # Log opcional no servidor (Render mostra isso)
        print("Erro ao falar com OpenAI:", e)

        # Resposta amigável para a Audrey
        fallback = (
            "Ai, eu tive um errinho aqui dentro agora 😅. "
            "Pode tentar de novo em alguns segundinhos? "
            "Enquanto isso, a gente pode pensar em outra coisa legal pra conversar! 💜"
        )
        return {"reply": fallback}
