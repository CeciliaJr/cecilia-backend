# Cecília Backend — A irmã virtual da Audrey 💜

## Como rodar localmente:
1. instale as dependências:
   pip install -r requirements.txt

2. exporte a chave:
   export OPENAI_API_KEY="SUA_CHAVE_AQUI"

3. rode:
   uvicorn app:app --reload

## Deploy no Render
- Crie um novo Web Service
- Python 3.11
- Build command:
    pip install -r requirements.txt
- Start command:
    uvicorn app:app --host 0.0.0.0 --port 10000
- Plano Free
