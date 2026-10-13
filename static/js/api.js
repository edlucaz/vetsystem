/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/api.js
 * Função     : Cliente mínimo da API REST (fetch + sessão do Django + CSRF) e utilidades de data/anúncio.
 * Fluxograma : apoio a todas as etapas que usam a API
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-13
 */
(function () {
  'use strict';

  function tokenCsrf() {
    var cookie = document.cookie.split('; ').find(function (c) { return c.indexOf('csrftoken=') === 0; });
    if (cookie) return decodeURIComponent(cookie.split('=')[1]);
    var campo = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return campo ? campo.value : '';
  }

  async function requisitar(url, metodo, corpo, opcoes) {
    var cabecalhos = { 'Accept': 'application/json' };
    if (metodo !== 'GET') {
      cabecalhos['Content-Type'] = 'application/json';
      cabecalhos['X-CSRFToken'] = tokenCsrf();
    }
    var resposta = await fetch(url, Object.assign({
      method: metodo, headers: cabecalhos, credentials: 'same-origin',
      body: corpo === undefined ? undefined : JSON.stringify(corpo)
    }, opcoes || {}));
    var dados = null;
    if (resposta.status !== 204) {
      try { dados = await resposta.json(); } catch (e) { dados = null; }
    }
    if (!resposta.ok) {
      var erro = new Error('Erro ' + resposta.status + ' em ' + url);
      erro.status = resposta.status;
      erro.dados = dados;
      throw erro;
    }
    return dados;
  }

  /* Converte o formato de erro do DRF ({campo: [mensagens]}) numa lista de textos. */
  function mensagens(dados) {
    if (!dados) return ['Não foi possível concluir a operação. Tente novamente.'];
    if (typeof dados === 'string') return [dados];
    if (Array.isArray(dados)) return dados.map(String);
    var lista = [];
    Object.keys(dados).forEach(function (campo) {
      var valor = dados[campo];
      (Array.isArray(valor) ? valor : [valor]).forEach(function (m) { lista.push(String(m)); });
    });
    return lista;
  }

  /* Anuncia uma mensagem para leitores de tela (região viva #anuncios, em base.html). */
  function anunciar(texto) {
    var regiao = document.getElementById('anuncios');
    if (!regiao) return;
    regiao.textContent = '';
    window.setTimeout(function () { regiao.textContent = texto; }, 50);
  }

  /* Data LOCAL em AAAA-MM-DD — nunca use toISOString(), que converte para UTC. */
  function dataIso(data) {
    return data.getFullYear() + '-' + String(data.getMonth() + 1).padStart(2, '0') + '-' +
      String(data.getDate()).padStart(2, '0');
  }

  function dataDeIso(texto) {
    var p = texto.split('-').map(Number);
    return new Date(p[0], p[1] - 1, p[2]);
  }

  var DIAS = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'];

  function dataPorExtenso(data) {  // "terça-feira, 14/10"
    return DIAS[data.getDay()] + ', ' + String(data.getDate()).padStart(2, '0') + '/' +
      String(data.getMonth() + 1).padStart(2, '0');
  }

  window.VetAPI = {
    get: function (url, opcoes) { return requisitar(url, 'GET', undefined, opcoes); },
    post: function (url, corpo, opcoes) { return requisitar(url, 'POST', corpo, opcoes); },
    patch: function (url, corpo) { return requisitar(url, 'PATCH', corpo); },
    mensagens: mensagens, anunciar: anunciar, dataIso: dataIso, dataDeIso: dataDeIso,
    dataPorExtenso: dataPorExtenso,
    DIAS_CURTOS: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
  };
}());
