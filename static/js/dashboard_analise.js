/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/dashboard_analise.js
 * Função     : Painel "Análise de dados" do dashboard — cards, gráficos (Chart.js) com tabela
 *              gêmea e ocupação da agenda por dia da semana, a partir de GET /api/estatisticas/.
 * Fluxograma : apoio à gestão (indicadores das consultas registradas)
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-23
 */
(function () {
  'use strict';

  var secao = document.getElementById('analise-dados');
  if (!secao || !window.VetAPI) return;

  var COR_SERIE = '#6848A1', COR_HOVER = '#563A8C', COR_GRADE = '#E5E7EB', COR_EIXO = '#4B5563', COR_ROTULO = '#1B1B1B';
  var COR_TRILHA = '#EAE4FA';
  var semAnimacao = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

  var periodo = document.getElementById('periodo-analise');
  var conteudo = document.getElementById('analise-conteudo');
  var erro = document.getElementById('analise-erro');
  var vazio = document.getElementById('analise-vazio');
  var graficos = {};

  var rotuloNaPonta = { id: 'rotuloNaPonta', afterDatasetsDraw: function (g) {
    var ctx = g.ctx, horizontal = g.options.indexAxis === 'y';
    ctx.save(); ctx.fillStyle = COR_ROTULO; ctx.font = '600 12px Lato, sans-serif';
    g.getDatasetMeta(0).data.forEach(function (barra, i) {
      var v = g.data.datasets[0].data[i]; if (!v) return;
      if (horizontal) { ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(String(v), barra.x + 6, barra.y); }
      else { ctx.textAlign = 'center'; ctx.textBaseline = 'bottom'; ctx.fillText(String(v), barra.x, barra.y - 4); }
    }); ctx.restore(); } };

  function desenharBarras(id, rotulos, valores, horizontal) {
    if (!window.Chart) return null;  // CDN fora do ar: ficam os cards e as tabelas
    if (graficos[id]) graficos[id].destroy();
    var eixoValor = { beginAtZero: true, grid: { color: COR_GRADE }, border: { display: false }, ticks: { color: COR_EIXO, precision: 0 } };
    var eixoCat = { grid: { display: false }, border: { color: COR_GRADE }, ticks: { color: COR_EIXO } };
    var canvas = document.getElementById(id);
    var grafico = new Chart(canvas, { type: 'bar',
      data: { labels: rotulos, datasets: [{ data: valores, backgroundColor: COR_SERIE, hoverBackgroundColor: COR_HOVER,
              maxBarThickness: 24, borderRadius: 4, borderSkipped: 'start' }] },
      options: { indexAxis: horizontal ? 'y' : 'x', responsive: true, maintainAspectRatio: false,
        animation: semAnimacao ? false : { duration: 300 },
        layout: { padding: { top: horizontal ? 0 : 20, right: horizontal ? 36 : 0 } },
        plugins: { legend: { display: false }, tooltip: { displayColors: false } },
        scales: horizontal ? { x: eixoValor, y: eixoCat } : { x: eixoCat, y: eixoValor } },
      plugins: [rotuloNaPonta] });
    canvas.setAttribute('aria-label', canvas.dataset.titulo + ': ' + rotulos.map(function (r, i) { return r + ' ' + valores[i]; }).join('; ') + '.');
    graficos[id] = grafico;
    return grafico;
  }

  function rotuloMes(chave) {  // "2026-05" → "mai/26"
    var p = chave.split('-');
    return MESES[Number(p[1]) - 1] + '/' + p[0].slice(2);
  }

  function numero(n) { return Number(n).toLocaleString('pt-BR'); }

  function preencherTabela(id, rotulos, valores) {
    var corpo = document.querySelector('#' + id + ' tbody');
    corpo.replaceChildren();
    rotulos.forEach(function (rotulo, i) {
      var linha = document.createElement('tr');
      var th = document.createElement('th');
      th.scope = 'row'; th.className = 'text-left font-normal py-1'; th.textContent = rotulo;
      var td = document.createElement('td');
      td.className = 'text-right py-1'; td.textContent = numero(valores[i]);
      linha.append(th, td);
      corpo.appendChild(linha);
    });
  }

  function horas(minutos) { return numero(Math.round(minutos / 60)) + ' h'; }

  function preencherOcupacao(dias) {
    var lista = document.getElementById('lista-ocupacao');
    lista.replaceChildren();
    dias.forEach(function (d) {
      var item = document.createElement('li');
      var texto = document.createElement('p');
      texto.className = 'text-sm mb-1';
      texto.style.color = COR_ROTULO;
      texto.textContent = d.rotulo + ' — ' + numero(Math.round(d.percentual)) + '% (' +
        horas(d.minutos_agendados) + ' de ' + horas(d.minutos_disponiveis) + ')';
      var trilha = document.createElement('div');
      trilha.setAttribute('aria-hidden', 'true');
      trilha.className = 'h-3 rounded';
      trilha.style.background = COR_TRILHA;
      var barra = document.createElement('div');
      barra.className = 'h-3 rounded';
      barra.style.background = COR_SERIE;
      barra.style.width = Math.min(100, d.percentual) + '%';
      trilha.appendChild(barra);
      item.append(texto, trilha);
      lista.appendChild(item);
    });
  }

  async function carregar() {
    conteudo.classList.add('opacity-50');
    erro.hidden = true;
    try {
      var dados = await VetAPI.get(secao.dataset.url + '?meses=' + encodeURIComponent(periodo.value));
      document.getElementById('kpi-total').textContent = numero(dados.total_consultas);
      document.getElementById('kpi-cancelamento').textContent = numero(dados.taxa_cancelamento) + '%';
      document.getElementById('kpi-ocupacao').textContent = numero(dados.ocupacao_media) + '%';
      var maisProcurado = dados.por_tipo.reduce(function (a, b) { return b.total > a.total ? b : a; }, dados.por_tipo[0]);
      document.getElementById('kpi-tipo').textContent = dados.total_consultas && maisProcurado ? maisProcurado.rotulo : '—';
      vazio.hidden = dados.total_consultas > 0;

      var rotulosMes = dados.por_mes.map(function (m) { return rotuloMes(m.mes); });
      var valoresMes = dados.por_mes.map(function (m) { return m.total; });
      desenharBarras('grafico-mes', rotulosMes, valoresMes, false);
      preencherTabela('tabela-mes', rotulosMes, valoresMes);

      var rotulosTipo = dados.por_tipo.map(function (t) { return t.rotulo; });
      var valoresTipo = dados.por_tipo.map(function (t) { return t.total; });
      desenharBarras('grafico-tipo', rotulosTipo, valoresTipo, true);
      preencherTabela('tabela-tipo', rotulosTipo, valoresTipo);

      preencherOcupacao(dados.ocupacao_por_dia);
      VetAPI.anunciar('Análise atualizada: ' + numero(dados.total_consultas) + ' consultas no período.');
    } catch (e) {
      erro.textContent = 'Não foi possível carregar a análise de dados. Tente novamente.';
      erro.hidden = false;
    } finally {
      conteudo.classList.remove('opacity-50');
    }
  }

  periodo.addEventListener('change', carregar);
  carregar();
}());
