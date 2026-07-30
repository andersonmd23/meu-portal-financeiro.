import time
import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Infraestrutura Financeira Blindada Autonoma")

# Habilita conexoes de rede abertas e seguras
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Banco de dados temporario em memoria RAM para o Cache
cache_dados = {}
CACHE_EXPIRATION_SECONDS = 30  # Atualizacao dinamica rapida para testes rápidos

# Precos base realistas para os ativos simulados de forma independente
PRECOS_BASE = {
    "PETR4": 38.50,
    "VALE3": 62.20,
    "MGLU3": 12.40,
    "ITUB4": 34.80
}

# Mapeamento absoluto do diretorio de arquivos locais na nuvem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def gerar_cotacao_estavel(ticker: str):
    tempo_atual = time.time()
    
    # 1. Se a cotacao estiver no cache e for recente, consome o dado salvo
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
            
    # 2. Se o cache expirou, gera uma variacao controlada de mercado realista
    if ticker in PRECOS_BASE:
        preco_base = PRECOS_BASE[ticker]
        # Aplica uma pequena oscilacao de mercado de ate 0.5% para simular o tempo real
        variacao = random.uniform(-0.005, 0.005)
        novo_preco = round(preco_base * (1 + variacao), 2)
        
        # Salva a nova cotacao estruturada no cache interno
        cache_dados[ticker] = {
            "preco": novo_preco,
            "updated_at": tempo_atual
        }
        
        return {
            "ticker": ticker,
            "preco": novo_preco,
            "fonte": "Fonte Externa (Nova Requisicao)",
            "tempo_restante_cache_segundos": CACHE_EXPIRATION_SECONDS
        }
    else:
        raise HTTPException(status_code=404, detail=f"Ativo {ticker} nao cadastrado no barramento.")

# ROTA DA API: Fornece as cotacoes estruturadas
@app.get("/api/cotacao/{ticker}")
def obter_cotacao(ticker: str):
    ticker_limpo = ticker.upper().strip().replace(".SA", "")
    return gerar_cotacao_estavel(ticker_limpo)

# ROTA DO SITE: Serve o painel visual index.html contornando erros de extensao externa
@app.get("/")
def carregar_site_principal():
    # Testa os dois caminhos possíveis (index.html ou index.html.txt) para blindar o carregamento
    opcoes_caminho = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(STATIC_DIR, "index.html.txt")
    ]
    for caminho in opcoes_caminho:
        if os.path.exists(caminho):
            return FileResponse(caminho)
            
    raise HTTPException(status_code=404, detail="Arquivo visual do site nao localizado na pasta static.")

# Vincula a pasta static de forma resiliente
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


