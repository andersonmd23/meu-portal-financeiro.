import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import urllib.request
import json

app = FastAPI(title="Infraestrutura Financeira Blindada")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache_dados = {}
CACHE_EXPIRATION_SECONDS = 900  # 15 minutos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def consultar_provedor_brapi(ticker: str):
    tempo_atual = time.time()
    
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
            
    try:
        # ENDPOINT CORRIGIDO CONFORME A DOCUMENTAÇÃO V2 DA BRAPI
        url = f"https://brapi.dev{ticker}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            dados_resposta = json.loads(response.read().decode())
            
        # A brapi responde os dados encapsulados dentro de 'results' na primeira posição [0]
        dados_ativo = dados_resposta["results"][0]
        preco_atual = dados_ativo["regularMarketPrice"]
        
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
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Erro ao processar cotacao para {ticker}.")

@app.get("/api/cotacao/{ticker}")
def obtener_cotacao(ticker: str):
    ticker_limpo = ticker.upper().strip().replace(".SA", "")
    return consultar_provedor_brapi(ticker_limpo)

@app.get("/")
def carregar_site_principal():
    caminho_html = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(caminho_html):
        return FileResponse(caminho_html)
    raise HTTPException(status_code=404, detail="Arquivo index.html nao encontrado na pasta static.")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
