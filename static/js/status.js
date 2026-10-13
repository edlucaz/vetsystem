/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/status.js
 * Função     : Ações rápidas de status via POST /api/consultas/<id>/status/.
 * Fluxograma : "Confirmar agendamento (avisa o tutor)" e "Realizar atendimento ou registrar ausência → Atualizar status"
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-13
 */
(function () {
  'use strict';
  if (!window.VetAPI) return;
  var base = document.body.dataset.urlApiConsultas;               // "/api/consultas/"
  var TRANSICOES = { agendado: ['confirmado', 'realizado', 'cancelado'], confirmado: ['realizado', 'cancelado'],
                     realizado: [], cancelado: [] };

  function atualizarTela(consulta) {
    document.querySelectorAll('[data-status-badge="' + consulta.id + '"]').forEach(function (selo) {
      selo.className = 'badge badge-' + consulta.status;
      selo.textContent = consulta.status_display;
    });
    document.querySelectorAll('[data-acoes-consulta="' + consulta.id + '"]').forEach(function (grupo) {
      var permitidos = TRANSICOES[consulta.status] || [];
      if (!permitidos.length) { grupo.hidden = true; return; }
      grupo.querySelectorAll('[data-acao-status]').forEach(function (b) {
        b.hidden = permitidos.indexOf(b.dataset.acaoStatus) === -1;
      });
      grupo.querySelectorAll('[data-confirmar-consulta]').forEach(function (a) { a.dataset.statusAtual = consulta.status; });
    });
  }

  function mudarStatus(id, status, observacao, opcoes) {
    return VetAPI.post(base + id + '/status/', { status: status, observacao: observacao || '' }, opcoes)
      .then(function (consulta) {
        atualizarTela(consulta);
        VetAPI.anunciar('Status atualizado para ' + consulta.status_display + '.');
        return consulta;
      })
      .catch(function (erro) {
        var texto = VetAPI.mensagens(erro.dados).join(' ');
        document.querySelectorAll('[data-erro-acoes="' + id + '"]').forEach(function (p) { p.textContent = texto; });
        VetAPI.anunciar(texto);
      });
  }

  document.addEventListener('click', function (evento) {
    var botao = evento.target.closest('[data-acao-status]');
    if (botao) {
      botao.disabled = true;
      mudarStatus(botao.dataset.consultaId, botao.dataset.acaoStatus, botao.dataset.observacao)
        .finally(function () { botao.disabled = false; });
      return;
    }
    var link = evento.target.closest('[data-confirmar-consulta]');
    if (link && link.dataset.statusAtual === 'agendado') {
      // Não cancela o clique: o WhatsApp abre em nova aba e a confirmação segue em paralelo.
      mudarStatus(link.dataset.confirmarConsulta, 'confirmado', 'Tutor avisado pelo WhatsApp.', { keepalive: true });
    }
  });
}());
