pythonimport time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf

app = FastAPI(title="Infraestrutura Financeira Unificada")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache_dados = {}
CACHE_EXPIRATION_SECONDS = 900  # 15 minutos

def consultar_provedor_financeiro(ticker: str):
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
        ativo = yf.Ticker(ticker)
        preco_atual = ativo.fast_info['last_price']
        
        if preco_atual is None or preco_atual <= 0:
            raise ValueError()
            
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
        raise HTTPException(status_code=404, detail=f"Ativo {ticker} invalido.")

@app.get("/api/cotacao/{ticker}")
def obtener_cotacao(ticker: str):
    return consultar_provedor_financeiro(ticker.upper().strip())

@app.get("/")
def carregar_site_principal():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")
