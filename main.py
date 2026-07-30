
import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf

app = FastAPI(title="Infraestrutura Financeira Unificada")

# Habilita conexões externas seguras
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Banco de dados em memória RAM para o Cache
cache_dados = {}
CACHE_EXPIRATION_SECONDS = 900  # Tempo de proteção: 15 minutos

# Descobre o caminho exato da pasta atual no servidor da nuvem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def consultar_provedor_financeiro(ticker: str):
    tempo_atual = time.time()
    
    # Valida se a informação está no cache e ainda é válida
    if ticker in cache_dados:
        dados_salvos = cache_dados[ticker]
        idade_do_cache = tempo_atual - dados_salvos["updated_at"]
        if idade_do_cache < CACHE_EXPIRATION_SECONDS:
            return {
                "ticker": ticker,
                "preco": dados_salvos["preco"],
                "fonte": "Cache Interno Protegido",
                "tempo_restante_cache_segundos": int(CACHE_EXPIRATION_SECONDS - idade_do_cache)
            }
            
    # Executa a busca externa se o cache expirou ou não existir
    try:
        ativo = yf.Ticker(ticker)
        preco_atual = ativo.fast_info['last_price']
        
        if preco_atual is None or preco_atual <= 0:
            raise ValueError()
            
        # Salva o resultado no banco interno antes de responder
        cache_dados[ticker] = {
            "preco": round(preco_atual, 2),
            "updated_at": tempo_atual
        }
        
        return {
            "ticker": ticker,
            "preco": round(preco_atual, 2),
            "fonte": "Fonte Externa (Nova Requisicao)",
            "tempo_restante_cache_segundos": CACHE_EXPIRATION_SECONDS
        }
        
    except Exception:
        raise HTTPException(status_code=404, detail=f"Ativo {ticker} invalido ou indisponivel.")

# ROTA DA API: O site consome este endpoint internamente
@app.get("/api/cotacao/{ticker}")
def obter_cotacao(ticker: str):
    return consultar_provedor_financeiro(ticker.upper().strip())

# ROTA DO SITE: Entrega a página principal de forma segura
@app.get("/")
def carregar_site_principal():
    caminho_html = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(caminho_html):
        return FileResponse(caminho_html)
    raise HTTPException(status_code=404, detail="Arquivo index.html nao encontrado na pasta static.")

# Vincula a pasta static usando o caminho absoluto blindado
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

