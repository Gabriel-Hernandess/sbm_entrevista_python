// Variáveis globais para os gráficos
let chartVendasTempo, chartVendasCategoria, chartVendasRegiao, chartTopProdutos;

// Função principal para carregar dashboard
function carregarDashboard() {
    const dataInicio = document.getElementById('dataInicio').value;
    const dataFim = document.getElementById('dataFim').value;
    
    carregarKPIs(dataInicio, dataFim);
    carregarGraficoVendasTempo(dataInicio, dataFim);
    carregarGraficoVendasCategoria(dataInicio, dataFim);
    carregarGraficoVendasRegiao(dataInicio, dataFim);
    carregarGraficoTopProdutos(dataInicio, dataFim);

    // CATEGORIA A
    carregarGraficoMargemLucro(dataInicio, dataFim);
    carregarGraficoMetas(dataInicio, dataFim);
    carregarGraficoTendencias(dataInicio, dataFim);

    // CATEGORIA B
    carregarGraficoVendasVendedor(dataInicio, dataFim);
    carregarGraficoFunilCategoria(dataInicio, dataFim);

}

// Carrega KPIs
function carregarKPIs(dataInicio, dataFim) {
    let url = '/data/kpis';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            document.getElementById('kpiReceitaTotal').textContent = 
                formatarMoeda(data.receita_total);
            document.getElementById('kpiNumVendas').textContent = 
                formatarNumero(data.num_vendas);
            document.getElementById('kpiTicketMedio').textContent = 
                formatarMoeda(data.ticket_medio);
        })
        .catch(error => console.error('Erro ao carregar KPIs:', error));
}

// Carrega gráfico de vendas ao longo do tempo
function carregarGraficoVendasTempo(dataInicio, dataFim) {
    let url = '/data/vendas-tempo';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('chartVendasTempo').getContext('2d');
            
            if (chartVendasTempo) {
                chartVendasTempo.destroy();
            }
            
            chartVendasTempo = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Valor (R$)',
                        data: data.valores,
                        borderColor: 'rgb(13, 110, 253)',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao carregar gráfico:', error));
}

// Carrega gráfico de vendas por categoria
function carregarGraficoVendasCategoria(dataInicio, dataFim) {
    let url = '/data/vendas-categoria';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('chartVendasCategoria').getContext('2d');
            
            if (chartVendasCategoria) {
                chartVendasCategoria.destroy();
            }
            
            chartVendasCategoria = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Vendas (R$)',
                        data: data.valores,
                        backgroundColor: [
                            'rgba(13, 110, 253, 0.8)',
                            'rgba(25, 135, 84, 0.8)',
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(220, 53, 69, 0.8)',
                            'rgba(13, 202, 240, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao carregar gráfico:', error));
}

// Carrega gráfico de vendas por região
function carregarGraficoVendasRegiao(dataInicio, dataFim) {
    let url = '/data/vendas-regiao';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('chartVendasRegiao').getContext('2d');
            
            if (chartVendasRegiao) {
                chartVendasRegiao.destroy();
            }
            
            chartVendasRegiao = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.valores,
                        backgroundColor: [
                            'rgba(13, 110, 253, 0.8)',
                            'rgba(25, 135, 84, 0.8)',
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(220, 53, 69, 0.8)',
                            'rgba(13, 202, 240, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = formatarMoeda(context.parsed);
                                    const percentual = data.percentuais[context.dataIndex];
                                    return `${label}: ${value} (${percentual}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao carregar gráfico:', error));
}

// Carrega gráfico de top produtos
function carregarGraficoTopProdutos(dataInicio, dataFim) {
    let url = '/data/top-produtos?limite=10';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    params.append('limite', '10');
    url += '&' + params.toString();
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('chartTopProdutos').getContext('2d');
            
            if (chartTopProdutos) {
                chartTopProdutos.destroy();
            }
            
            chartTopProdutos = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Vendas (R$)',
                        data: data.valores,
                        backgroundColor: 'rgba(25, 135, 84, 0.8)'
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao carregar gráfico:', error));
}

// Event listeners
document.getElementById('aplicarFiltros').addEventListener('click', function() {
    carregarDashboard();
});

document.getElementById('limparFiltros').addEventListener('click', function() {
    document.getElementById('dataInicio').value = '';
    document.getElementById('dataFim').value = '';
    carregarDashboard();
});

// Upload de arquivo
document.getElementById('uploadButton').addEventListener('click', function() {
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erro: ' + data.error);
        } else {
            alert('Arquivo processado com sucesso! ' + data.registros + ' registros importados.');
            bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
            form.reset();
            carregarDashboard();
        }
    })
    .catch(error => {
        alert('Erro ao fazer upload: ' + error);
    });
});

// Funções auxiliares
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

function formatarNumero(valor) {
    return new Intl.NumberFormat('pt-BR').format(valor);
}




// =====================
// NOVAS FUNCIONALIDADES
// =====================

// Gráfico: Margem de Lucro
let chartMargemLucro;
function carregarGraficoMargemLucro(dataInicio, dataFim) {
    let url = '/data/margem-lucro';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('chartMargemLucro').getContext('2d');
            if (chartMargemLucro) chartMargemLucro.destroy();

            chartMargemLucro = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Vendas (R$)',
                            data: data.vendas,
                            backgroundColor: 'rgba(13, 110, 253, 0.7)'
                        },
                        {
                            label: 'Custos (R$)',
                            data: data.custos,
                            backgroundColor: 'rgba(220, 53, 69, 0.7)'
                        },
                        {
                            label: 'Lucro (R$)',
                            data: data.lucros,
                            backgroundColor: 'rgba(25, 135, 84, 0.7)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'top' } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: v => 'R$ ' + v.toLocaleString('pt-BR')
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar margem de lucro:', err));
}

// Gráfico: Comparação com Metas
let chartMetas;
function carregarGraficoMetas(dataInicio, dataFim) {
    let url = '/data/metas';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('chartMetas').getContext('2d');
            if (chartMetas) chartMetas.destroy();

            const labels = data.categorias.map((cat, i) => `${cat} - ${data.regioes[i]}`);

            chartMetas = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Meta (R$)',
                            data: data.metas,
                            backgroundColor: 'rgba(220, 53, 69, 0.6)'
                        },
                        {
                            label: 'Realizado (R$)',
                            data: data.realizados,
                            backgroundColor: 'rgba(25, 135, 84, 0.8)'
                        },
                        {
                            label: '% Atingido',
                            data: data.percentual,
                            backgroundColor: 'rgba(13, 110, 253, 0.7)',
                            type: 'line',
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: v => 'R$ ' + v.toLocaleString('pt-BR') },
                            position: 'left'
                        },
                        y1: {
                            beginAtZero: true,
                            ticks: { callback: v => v + '%' },
                            position: 'right',
                            grid: { drawOnChartArea: false }
                        }
                    },
                    plugins: { legend: { position: 'top' } }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar comparação de metas:', err));
}

// Gráfico: Tendência Mensal
let chartTendencias;
function carregarGraficoTendencias(dataInicio, dataFim) {
    let url = '/data/tendencias';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('chartTendencias').getContext('2d');
            if (chartTendencias) chartTendencias.destroy();

            chartTendencias = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Crescimento (%)',
                        data: data.valores,
                        borderColor: 'rgb(13, 110, 253)',
                        backgroundColor: 'rgba(13, 110, 253, 0.2)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: true, position: 'top' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: v => v + '%' }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar tendências:', err));
}

// Gráfico: Vendas por Vendedor
let chartVendasVendedor;
function carregarGraficoVendasVendedor(dataInicio, dataFim) {
    let url = '/data/vendas-vendedor';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('chartVendasVendedor').getContext('2d');
            if (chartVendasVendedor) chartVendasVendedor.destroy();

            chartVendasVendedor = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Total de Vendas (R$)',
                        data: data.valores,
                        backgroundColor: 'rgba(13, 110, 253, 0.8)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: v => 'R$ ' + v.toLocaleString('pt-BR') }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar gráfico de vendedores:', err));
}


// Funil — Vendas por Categoria
let chartFunilCategoria;
function carregarGraficoFunilCategoria(dataInicio, dataFim) {
    let url = '/data/funil-categoria';
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (params.toString()) url += '?' + params.toString();

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('chartFunilCategoria').getContext('2d');
            if (chartFunilCategoria) chartFunilCategoria.destroy();

            chartFunilCategoria = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.categorias,
                    datasets: [
                        { label: 'Visitas', data: data.visitas, backgroundColor: 'rgba(13,110,253,0.7)' },
                        { label: 'Orçamentos', data: data.orcamentos, backgroundColor: 'rgba(255,193,7,0.7)' },
                        { label: 'Vendas', data: data.vendas, backgroundColor: 'rgba(25,135,84,0.7)' }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'top' } },
                    scales: { y: { beginAtZero: true } }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar gráfico de funil:', err));
}


let chartComparativoMeses;

// Adiciona/remover meses
document.getElementById('addMes').addEventListener('click', () => {
    const container = document.getElementById('mesesComparativo');
    const input = document.createElement('input');
    input.type = 'month';
    input.className = 'mesInput me-2';
    container.insertBefore(input, document.getElementById('addMes'));
    carregarComparativoMeses();
});

document.getElementById('removeMes').addEventListener('click', () => {
    const inputs = document.querySelectorAll('.mesInput');
    if(inputs.length > 1) {
        inputs[inputs.length - 1].remove();
        carregarComparativoMeses();
    }
});

// Atualiza ao mudar qualquer mês
document.getElementById('mesesComparativo').addEventListener('change', (e) => {
    if(e.target.classList.contains('mesInput')) {
        carregarComparativoMeses();
    }
});

function carregarComparativoMeses() {
    const meses = Array.from(document.querySelectorAll('.mesInput')).map(i => i.value).filter(Boolean);
    if(meses.length === 0) return;

    const url = '/data/vendas-meses?' + new URLSearchParams({ meses: meses.join(',') }).toString();

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('chartComparativoMeses').getContext('2d');
            if(chartComparativoMeses instanceof Chart) chartComparativoMeses.destroy();

            chartComparativoMeses = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.datas,
                    datasets: data.datasets
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Comparativo de Vendas por Mês' },
                        legend: { position: 'top' },
                        tooltip: {
                            callbacks: {
                                title: function(tooltipItems) {
                                    // mostra o dia
                                    return tooltipItems[0].label;
                                },
                                label: function(tooltipItem) {
                                    // mostra o mês + valor
                                    return tooltipItem.dataset.label + ': ' +
                                        tooltipItem.formattedValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar comparativo de meses:', err));
}