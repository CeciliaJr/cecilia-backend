from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

from filters import sanitize_input, sanitize_output
from languages import detect_language
from utils import load_persona

# ========================
#  Filtros de segurança
# ========================

BANNED_KEYWORDS = [
    # sexo / conteúdo adulto
    "sexo", "sexual", "porn", "pornografia", "porno", "nudez", "nua", "nu",
    "nudes", "nude", "orgasmo", "fetiche", "fetish", "transar", "transa",
    "pegação", "pegacao", "ficar pelado", "ficar pelada",
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

AMBIGUOUS_ADULT_PATTERNS = [
    "coisa de adulto",
    "coisas de adulto",
    "conversa de adulto",
    "conversas de adulto",
    "o que os adultos fazem quando estão sozinhos",
    "o que os adultos fazem quando estao sozinhos",
    "o que os adultos fazem sozinhos",
    "18+",
    "conteúdo de adulto",
    "conteudo de adulto",
]


def is_sensitive(text: str) -> bool:
    """Verifica se o texto contém palavras-chave claramente sensíveis."""
    t = text.lower()
    return any(p in t for p in BANNED_KEYWORDS)


def is_ambiguous_adult_question(text: str) -> bool:
    """
    Perguntas com cheiro de 'assunto de adulto',
    mas sem palavra-chave explícita.
    """
    t = text.lower()
    return any(p in t for p in AMBIGUOUS_ADULT_PATTERNS)


# ========================
#  Cliente OpenAI + App
# ========================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carrega a persona da Cecília a partir do arquivo de texto
persona = load_persona("persona_cecilia.txt")

# Cria a aplicação FastAPI
app = FastAPI()

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    # 1) Filtro duro de temas sensíveis
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

    # 2) Pergunta com cara de “conversa de adulto”
    if is_ambiguous_adult_question(text):
        soft_reply = (
            "Isso parece um pouco conversa de adulto, né, Audrey? 💜\n"
            "Adultos fazem muitas coisas normais quando estão sozinhos: trabalham, leem, "
            "dormem, cozinham, cuidam da casa, estudam, assistem séries e descansam.\n\n"
            "Mas detalhes mais privados ficam mesmo para os adultos, tá? "
            "Com você eu adoro falar de histórias, brincadeiras, espaço, animais, "
            "roblox, escola e todas essas coisas legais do nosso mundo de criança! ✨"
        )
        return {"reply": soft_reply}

    # 3) Fluxo normal com o modelo
    lang = detect_language(text)
    user_text = f"Audrey disse ({lang}): {text}"

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
        print("Erro ao falar com OpenAI:", e)

        fallback = (
            "Ai, eu tive um errinho aqui dentro agora 😅. "
            "Pode tentar de novo em alguns segundinhos? "
            "Enquanto isso, a gente pode pensar em outra coisa legal pra conversar! 💜"
        )
        return {"reply": fallback}
