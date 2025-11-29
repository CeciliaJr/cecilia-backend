from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

from filters import sanitize_input, sanitize_output
from languages import detect_language
from utils import load_persona

# Cria o cliente da OpenAI usando a chave do ambiente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carrega a persona da Cecília a partir do arquivo de texto
persona = load_persona("persona_cecilia.txt")

# Cria a aplicação FastAPI
app = FastAPI()

# Configura CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # você pode restringir isso depois se quiser
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

    # Detecta idioma básico (pt/es/en)
    lang = detect_language(text)

    # Monta texto do usuário
    user_text = f"Audrey disse ({lang}): {text}"

    # Chama o modelo da OpenAI usando o cliente novo
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": user_text},
            ],
            max_tokens=200,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()
        reply = sanitize_output(reply)
        return {"reply": reply}

    except Exception as e:
        # Se der algum erro, devolve algo amigável pra não quebrar o frontend
        return {
            "reply": "Desculpa, Audrey 💜 Tive um errinho aqui por dentro. Pode tentar de novo em alguns segundinhos?"
        }
