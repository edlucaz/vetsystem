/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/horarios_publicos.js
 * Função     : Home pública — mostra os próximos horários livres (GET /api/horarios-publicos/);
 *              cada horário é um link de WhatsApp com a mensagem já preenchida.
 * Fluxograma : raia do Tutor — "Solicitar agendamento"
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-23
 */
(function () {
  'use strict';

  var secao = document.getElementById('horarios');
  if (!secao || !window.VetAPI) return;
  var conteudo = document.getElementById('horarios-conteudo');

  function linkWhatsapp(data, horario) {
    var dataCurta = String(data.getDate()).padStart(2, '0') + '/' + String(data.getMonth() + 1).padStart(2, '0');
    var a = document.createElement('a');
    a.href = 'https://wa.me/' + secao.dataset.whatsapp + '?text=' +
      encodeURIComponent('Olá! Gostaria de agendar um atendimento em ' + dataCurta + ' às ' + horario + ' para meu pet.');
    a.target = '_blank';
    a.rel = 'noopener';
    a.className = 'inline-block font-bold px-4 py-2 rounded-xl border-2 hover:opacity-90';
    a.style.borderColor = '#1E7579';
    a.style.color = '#1E7579';
    a.textContent = horario;
    var aviso = document.createElement('span');
    aviso.className = 'sr-only';
    aviso.textContent = ' — pedir este horário pelo WhatsApp (abre em nova aba)';
    a.appendChild(aviso);
    return a;
  }

  VetAPI.get(secao.dataset.url).then(function (dados) {
    if (!dados.dias.length) return;  // fica a mensagem do WhatsApp
    var fragmento = document.createDocumentFragment();
    dados.dias.forEach(function (dia) {
      var data = VetAPI.dataDeIso(dia.data);
      var h3 = document.createElement('h3');
      h3.className = 'font-bold text-gray-800 mt-4 mb-2';
      h3.textContent = VetAPI.dataPorExtenso(data);
      var ul = document.createElement('ul');
      ul.className = 'flex flex-wrap gap-2';
      dia.horarios.forEach(function (horario) {
        var li = document.createElement('li');
        li.appendChild(linkWhatsapp(data, horario));
        ul.appendChild(li);
      });
      fragmento.append(h3, ul);
    });
    var nota = document.createElement('p');
    nota.className = 'text-sm text-gray-600 mt-6';
    nota.textContent = 'Escolha um horário para combinar pelo WhatsApp (19) 98728-6814.';
    fragmento.appendChild(nota);
    conteudo.replaceChildren(fragmento);
  }).catch(function () { /* mantém a mensagem do WhatsApp */ });
}());
