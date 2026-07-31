/* ENGINE DE COMUNICAÇÃO DE REDE ASSEGURADA - LOOP ENGINEERED */
(function() {
    const tickers = ["PETR4", "VALE3", "MGLU3", "ITUB4"];
    
    async function requisitarAtivo(ticker) {
        try {
            const resposta = await fetch(`/api/cotacao/${ticker}`);
            if (!resposta.ok) throw new Error();
            const dados = await resposta.json();
            
            // Renderização segura dos preços e variações em porcentagem
            document.getElementById(`price-${ticker}`).innerText = `R$ ${dados.preco.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
            const elementoVariacao = document.getElementById(`v-${ticker}`);
            
            elementoVariacao.innerText = `${dados.variacao >= 0 ? '+' : ''}${dados.variacao.toFixed(2)}%`;
            elementoVariacao.style.color = dados.variacao >= 0 ? "#10b981" : "#ef4444";
        } catch (e) {
            document.getElementById(`price-${ticker}`).innerText = "Erro";
        }
    }

    function atualizarPainel() {
        tickers.forEach(t => requisitarAtivo(t));
    }

    // Exporta a função para o botão HTML acessar com segurança
    window.PortalEngine = { atualizarPainel };

    window.addEventListener('DOMContentLoaded', () => {
        atualizarPainel();
        setInterval(atualizarPainel, 12000); // Atualização assíncrona constante a cada 12 segundos
    });
})();
