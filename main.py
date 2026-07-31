import time
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="CapitalAberto Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache_dados = {}
CACHE_EXPIRATION_SECONDS = 15

BANCO_ATIVOS = {
    "PETR4": {"nome": "Petrobras PN", "base": 38.50},
    "VALE3": {"nome": "Vale ON", "base": 62.20},
    "MGLU3": {"nome": "Magazine Luiza ON", "base": 12.40},
    "ITUB4": {"nome": "Itaú Unibanco PN", "base": 34.80}
}

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
        variacao = random.uniform(-0.004, 0.004)
        preco_atual = round(info["base"] * (1 + variacao), 2)
        porcentagem = round(variacao * 100, 2)
        
        resposta = {
            "ticker": ticker_limpo,
            "nome": info["nome"],
            "preco": preco_atual,
            "variacao": porcentagem,
            "fonte": "Cache Interno Protegido",
            "tempo_restante_cache_segundos": CACHE_EXPIRATION_SECONDS
        }
        
        cache_dados[ticker_limpo] = {
            "dados": resposta,
            "updated_at": tempo_atual
        }
        return resposta
    
    raise HTTPException(status_code=404, detail="Ativo nao localizado.")

@app.get("/", response_class=HTMLResponse)
def carregar_site_principal():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CapitalAberto - Terminal de Mercados Globais</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
            body { background-color: #f1f5f9; color: #0f172a; overflow-x: hidden; }
            .ticker-tape-container { background: #1e293b; color: #ffffff; padding: 5px 0; min-height: 44px; width: 100%; border-bottom: 2px solid #f59e0b; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            header { background: #ffffff; padding: 20px 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; border-left: 6px solid #1e40af; }
            header h1 { color: #1e40af; font-size: 1.8rem; font-weight: 800; }
            header h1 span { color: #f59e0b; }
            .main-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 25px; }
            .section-title { font-size: 1.15rem; font-weight: 700; color: #1e3a8a; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }
            .widget-box { background: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 25px; }
            .grid-produtos { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
            .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.01); }
            .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
            .badge { font-size: 0.7rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
            .ticker-name { font-size: 0.95rem; font-weight: 700; color: #475569; }
            .preco-grande { font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 8px 0; }
            .footer-card { display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #94a3b8; border-top: 1px solid #f1f5f9; padding-top: 10px; margin-top: 10px; }
            .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block; margin-right: 4px; }
            .chart-container { height: 500px; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; }
            .sidebar { display: flex; flex-direction: column; gap: 5px; }
            .btn-refresh { padding: 10px 20px; background: #1e40af; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
            @media (max-width: 1024px) { .main-layout { grid-template-columns: 1fr; } .chart-container { height: 400px; } }
        </style>
    </head>
    <body>
        <div class="ticker-tape-container">
            <div class="tradingview-widget-container">
                <div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://tradingview.com" async>
                {
                    "symbols": [
                        {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"},
                        {"proName": "FX_IDC:USDBRL", "title": "Dólar / Real"},
                        {"proName": "FX_IDC:EURBRL", "title": "Euro / Real"},
                        {"proName": "BMFBOVESPA:IBOV", "title": "Ibovespa"}
                    ],
                    "showSymbolLogo": true, "colorTheme": "light", "isTransparent": false, "displayMode": "adaptive", "locale": "br"
                }
                </script>
            </div>
        </div>

        <div class="container">
            <header>
                <h1>CAPITAL<span>ABERTO</span></h1>
                <button class="btn-refresh" onclick="atualizarPainel()">Atualizar Painel</button>
            </header>

            <div class="main-layout">
                <div>
                    <div class="widget-box">
                        <div class="section-title">🖥️ Monitoramento de Ativos Locais (B3)</div>
                        <div class="grid-produtos">
                            <div class="card">
                                <div class="card-header"><span class="ticker-name">Petrobras (PETR4)</span><span class="badge">B3</span></div>
                                <div class="preco-grande" id="price-PETR4">R$ --,--</div>
                                <div class="footer-card"><span id="fonte-PETR4">Carregando...</span><span><span class="status-dot"></span>Dinamico</span></div>
                            </div>
                            <div class="card">
                                <div class="card-header"><span class="ticker-name">Vale (VALE3)</span><span class="badge">B3</span></div>
                                <div class="preco-grande" id="price-VALE3">R$ --,--</div>
                                <div class="footer-card"><span id="fonte-VALE3">Carregando...</span><span><span class="status-dot"></span>Dinamico</span></div>
                            </div>
                            <div class="card">
                                <div class="card-header"><span class="ticker-name">Magaz. Luiza (MGLU3)</span><span class="badge">B3</span></div>
                                <div class="preco-grande" id="price-MGLU3">R$ --,--</div>
                                <div class="footer-card"><span id="fonte-MGLU3">Carregando...</span><span><span class="status-dot"></span>Dinamico</span></div>
                            </div>
                            <div class="card">
                                <div class="card-header"><span class="ticker-name">Itaú (ITUB4)</span><span class="badge">B3</span></div>
                                <div class="preco-grande" id="price-ITUB4">R$ --,--</div>
                                <div class="footer-card"><span id="fonte-ITUB4">Carregando...</span><span><span class="status-dot"></span>Dinamico</span></div>
                            </div>
                        </div>
                    </div>

                    <div class="widget-box">
                        <div class="section-title">📈 Análise Avançada e Gráfico Técnico Interativo</div>
                        <div class="chart-container">
                            <div id="tv_advanced_chart"></div>
                            <script type="text/javascript" src="https://tradingview.com"></script>
                            <script type="text/javascript">
                            window.addEventListener('DOMContentLoaded', function() {
                                new TradingView.widget({
                                    "width": "100%", "height": "100%", "symbol": "BMFBOVESPA:IBOV",
                                    "interval": "D", "timezone": "America/Sao_Paulo", "theme": "light",
                                    "style": "1", "locale": "br", "container_id": "tv_advanced_chart"
                                });
                            });
                            </script>
                        </div>
                    </div>
                </div>

                <div class="sidebar">
                    <div class="widget-box">
                        <div class="section-title">💵 Câmbio & Commodities Críticas</div>
                        <div class="tradingview-widget-container">
                            <script type="text/javascript" src="https://tradingview.com" async>
                            {
                                "colorTheme": "light", "dateRange": "12M", "showChart": false, "locale": "br", "width": "100%", "height": "240",


