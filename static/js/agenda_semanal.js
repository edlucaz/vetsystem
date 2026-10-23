/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/agenda_semanal.js
 * Função     : Agenda semanal — navega entre semanas e desenha um bloco por dia com o
 *              expediente (Disponibilidade) e as consultas, a partir da API.
 * Fluxograma : etapa 4 — "Exibir agenda interativa" (visão da semana)
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-23
 */
(function () {
  'use strict';

  var secao = document.getElementById('agenda-semanal');
  if (!secao || !window.VetAPI) return;

  var titulo = document.getElementById('titulo-semana');
  var container = document.getElementById('dias-semana');
  var erro = document.getElementById('agenda-erro');
  var segunda = segundaDaSemana(new Date());
  var requisicao = 0;

  function segundaDaSemana(data) {
    var d = new Date(data.getFullYear(), data.getMonth(), data.getDate());
    d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    return d;
  }

  function somarDias(data, dias) {
    return new Date(data.getFullYear(), data.getMonth(), data.getDate() + dias);
  }

  function dd(n) { return String(n).padStart(2, '0'); }
  function diaMes(d) { return dd(d.getDate()) + '/' + dd(d.getMonth() + 1); }
  function hora(texto) { return texto.slice(0, 5); }  // "08:00:00" → "08:00"

  function horaLocal(iso) {
    var d = new Date(iso);
    return dd(d.getHours()) + ':' + dd(d.getMinutes());
  }

  function urlDetalhe(id) {
    return secao.dataset.urlDetalhe.replace(/\/0\/$/, '/' + id + '/');
  }

  function itemConsulta(c) {
    var li = document.createElement('li');
    var link = document.createElement('a');
    link.href = urlDetalhe(c.id);
    link.className = 'flex flex-wrap items-center justify-between gap-2 py-2 hover:underline';
    var texto = document.createElement('span');
    texto.className = 'text-gray-800';
    texto.textContent = horaLocal(c.data_hora) + ' · ' + c.animal_nome + ' (' + c.proprietario_nome + ') · ' + c.tipo_display;
    var selo = document.createElement('span');
    selo.className = 'badge badge-' + c.status;
    selo.textContent = c.status_display;
    link.append(texto, selo);
    li.appendChild(link);
    return li;
  }

  function desenhar(consultas, disponibilidades) {
    var porDia = {};
    consultas.forEach(function (c) {
      var chave = VetAPI.dataIso(new Date(c.data_hora));
      (porDia[chave] = porDia[chave] || []).push(c);
    });
    var expediente = {};  // dia_da_semana do Django: 0 = segunda
    disponibilidades.filter(function (d) { return d.ativo; }).forEach(function (d) { expediente[d.dia_da_semana] = d; });

    container.replaceChildren();
    for (var i = 0; i < 7; i++) {
      var data = somarDias(segunda, i);
      var chave = VetAPI.dataIso(data);
      var doDia = porDia[chave] || [];
      var disp = expediente[i];
      if (i >= 5 && !doDia.length && !disp) continue;  // sábado e domingo só se houver algo

      var bloco = document.createElement('section');
      bloco.className = 'bg-white rounded-2xl shadow-sm p-5';
      bloco.setAttribute('aria-labelledby', 'dia-' + chave);
      var h3 = document.createElement('h3');
      h3.id = 'dia-' + chave;
      h3.className = 'font-bold mb-2';
      h3.style.color = '#4A2C7A';
      h3.textContent = VetAPI.DIAS_CURTOS[data.getDay()] + ' ' + diaMes(data) + ' · ' +
        (disp ? hora(disp.hora_inicio) + '–' + hora(disp.hora_fim) : 'Fechado');
      bloco.appendChild(h3);

      if (doDia.length) {
        var ul = document.createElement('ul');
        ul.className = 'divide-y divide-gray-100 text-sm';
        doDia.forEach(function (c) { ul.appendChild(itemConsulta(c)); });
        bloco.appendChild(ul);
      } else {
        var p = document.createElement('p');
        p.className = 'text-sm text-gray-600';
        p.textContent = 'Sem consultas';
        bloco.appendChild(p);
      }
      container.appendChild(bloco);
    }
  }

  async function carregar() {
    var minha = ++requisicao;
    var domingo = somarDias(segunda, 6);
    titulo.textContent = 'Semana de ' + diaMes(segunda) + ' a ' + diaMes(domingo) + '/' + domingo.getFullYear();
    container.classList.add('opacity-50');
    erro.hidden = true;
    try {
      var url = secao.dataset.urlConsultas + '?inicio=' + VetAPI.dataIso(segunda) +
        '&fim=' + VetAPI.dataIso(domingo) + '&limit=200';
      var respostas = await Promise.all([VetAPI.get(url), VetAPI.get(secao.dataset.urlDisponibilidades)]);
      if (minha !== requisicao) return;  // o usuário já trocou de semana
      var consultas = respostas[0].results || respostas[0];
      desenhar(consultas, respostas[1]);
      VetAPI.anunciar(consultas.length + (consultas.length === 1 ? ' consulta' : ' consultas') + ' na semana');
    } catch (e) {
      if (minha !== requisicao) return;
      erro.textContent = 'Não foi possível carregar a agenda. Tente novamente.';
      erro.hidden = false;
    } finally {
      if (minha === requisicao) container.classList.remove('opacity-50');
    }
  }

  document.getElementById('semana-anterior').addEventListener('click', function () { segunda = somarDias(segunda, -7); carregar(); });
  document.getElementById('semana-hoje').addEventListener('click', function () { segunda = segundaDaSemana(new Date()); carregar(); });
  document.getElementById('semana-proxima').addEventListener('click', function () { segunda = somarDias(segunda, 7); carregar(); });
  carregar();
}());
