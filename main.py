import time
import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Enterprise Financial Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache_dados = {}
CACHE_EXPIRATION_SECONDS = 15

# Banco de dados de ativos expandido (Estilo Investing)
BANCO_ATIVOS = {
    "PETR4": {"nome": "Petrobras PN", "base": 38.50, "tipo": "Ações"},
    "VALE3": {"nome": "Vale ON", "base": 62.20, "tipo": "Ações"},
    "MGLU3": {"nome": "Magazine Luiza ON", "base": 12.40, "tipo": "Ações"},
    "ITUB4": {"nome": "Itaú Unibanco PN", "base": 34.80, "tipo": "Ações"},
    "BBAS3": {"nome": "Banco do Brasil ON", "base": 27.10, "tipo": "Ações"},
    "BBDC4": {"nome": "Bradesco PN", "base": 14.35, "tipo": "Ações"},
    "SANB11": {"nome": "Santander Brasil Unit", "base": 29.20, "tipo": "Ações"},
    "ABEV3": {"nome": "Ambev ON", "base": 12.15, "tipo": "Ações"},
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

@app.get("/api/cotacao/{ticker}")
def obter_cotacao(ticker: str):
    ticker_limpo = ticker.upper().strip()
    tempo_atual = time.time()
    
    if ticker_limpo in cache_dados:
        dados_salvos = cache_dados[ticker_limpo]
        if tempo_atual - dados_salvos["updated_at"] < CACHE_EXPIRATION_SECONDS:
            return dados_salvos["dados"]
            
    if ticker_limpo in BANCO_ATIVOS:
        info = BANCO_ATIVOS[ticker_limpo]
        variacao = random.uniform(-0.003, 0.003)
        preco_atual = round(info["base"] * (1 + variacao), 2)
        porcentagem = round(variacao * 100, 2)
        
        resposta = {
            "ticker": ticker_limpo,
            "nome": info["nome"],
            "preco": preco_atual,
            "variacao": porcentagem,
            "tipo": info["tipo"],
            "fonte": "Cache Interno Protegido",
            "tempo_restante_cache_segundos": CACHE_EXPIRATION_SECONDS
        }
        
        cache_dados[ticker_limpo] = {
            "dados": resposta,
            "updated_at": tempo_atual
        }
        return resposta
    
    raise HTTPException(status_code=404, detail="Ativo nao localizado.")

@app.get("/")
def carregar_site_principal():
    caminho_html = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(caminho_html):
        return FileResponse(caminho_html)
    raise HTTPException(status_code=404, detail="Portal offline: index.html nao encontrado.")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


