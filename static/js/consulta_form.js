/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/consulta_form.js
 * Função     : Agendamento sem recarregar (POST /api/consultas/), com melhoria progressiva.
 * Fluxograma : decisão "Horário disponível?" → "Registrar consulta"
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-13
 */
(function () {
  'use strict';
  var form = document.getElementById('form-consulta');
  if (!form || !window.VetAPI) return;
  var select = document.getElementById('id_animal');
  var blocos = {
    busca: document.getElementById('bloco-busca'), select: document.getElementById('bloco-select-animal'),
    agenda: document.getElementById('bloco-agenda'), dataHora: document.getElementById('bloco-data-hora')
  };
  blocos.busca.hidden = false; blocos.select.hidden = true;
  blocos.agenda.hidden = false; blocos.dataHora.hidden = true;

  var busca = new VetAutocomplete({
    campoId: 'campo-busca', listaId: 'lista-sugestoes', statusId: 'status-busca', selectId: 'id_animal',
    url: form.dataset.urlAnimais,
    aoFalhar: function () { blocos.busca.hidden = true; blocos.select.hidden = false; }
  });
  if (window.VetSeletor) {
    new VetSeletor({
      dialogoId: 'seletor-cadastro', abridorId: 'abrir-seletor',
      urlTutores: form.dataset.urlProprietarios, urlAnimais: form.dataset.urlAnimais,
      urlNovoAnimal: form.dataset.urlNovoAnimal,
      aoEscolher: function (animal) { busca.selecionar(animal); }
    });
  }
  if (select.selectedIndex > 0) document.getElementById('campo-busca').value = select.options[select.selectedIndex].text;

  var agenda = new VetAgenda({
    diasId: 'agenda-dias', horariosId: 'agenda-horarios', statusId: 'agenda-status', tituloId: 'agenda-titulo',
    anteriorId: 'agenda-anterior', proximoId: 'agenda-proximo', campoDataId: 'id_data_consulta',
    campoHoraId: 'id_hora_consulta', urlHorarios: form.dataset.urlHorarios,
    urlDisponibilidades: form.dataset.urlDisponibilidades, ignorarId: form.dataset.consultaId
  });
  agenda.iniciar().then(function (ok) { if (!ok) { blocos.agenda.hidden = true; blocos.dataHora.hidden = false; } });

  if (form.dataset.modo !== 'criar') return;                      // edição: POST do Django, mesma regra

  var botao = document.getElementById('btn-agendar');
  var caixaErros = document.getElementById('mensagens-form');

  function limparErros() {
    caixaErros.hidden = true; caixaErros.textContent = '';
    form.querySelectorAll('[data-erro-campo]').forEach(function (el) { el.textContent = ''; });
    form.querySelectorAll('[aria-invalid="true"]').forEach(function (el) { el.removeAttribute('aria-invalid'); });
  }

  function mostrarErros(dados) {
    var campos = { animal: 'campo-busca', tipo: 'id_tipo', observacoes: 'id_observacoes' };
    var gerais = [];
    Object.keys(dados || {}).forEach(function (campo) {
      var textos = VetAPI.mensagens(dados[campo]);
      var alvo = form.querySelector('[data-erro-campo="' + campo + '"]');
      if (alvo) {
        alvo.textContent = textos.join(' ');
        if (campos[campo]) document.getElementById(campos[campo]).setAttribute('aria-invalid', 'true');
      } else {
        gerais = gerais.concat(textos);
      }
    });
    caixaErros.hidden = false;                                     // mostra antes de escrever: role="alert" anuncia
    caixaErros.textContent = (gerais.length ? gerais : ['Corrija os campos indicados.']).join(' ');
    caixaErros.focus();
  }

  function mostrarSucesso(consulta) {
    var quando = new Date(consulta.data_hora);                     // ISO com fuso → horário local
    document.getElementById('sucesso-resumo').textContent =
      consulta.animal_nome + ' (tutor: ' + consulta.proprietario_nome + ') — ' + consulta.tipo_display + ' — ' +
      VetAPI.dataPorExtenso(quando) + '/' + quando.getFullYear() + ' às ' +
      String(quando.getHours()).padStart(2, '0') + ':' + String(quando.getMinutes()).padStart(2, '0') +
      '. Status: ' + consulta.status_display + '.';
    document.getElementById('sucesso-detalhe').href = form.dataset.urlDetalhe.replace('/0/', '/' + consulta.id + '/');
    var whatsapp = document.getElementById('sucesso-whatsapp');
    whatsapp.hidden = !consulta.link_whatsapp;
    if (consulta.link_whatsapp) {
      whatsapp.href = consulta.link_whatsapp;
      whatsapp.dataset.confirmarConsulta = String(consulta.id);
      whatsapp.dataset.statusAtual = consulta.status;
    }
    form.hidden = true;
    var painel = document.getElementById('painel-sucesso');
    painel.hidden = false;
    painel.focus();
    VetAPI.anunciar('Consulta agendada com sucesso.');
  }

  form.addEventListener('submit', async function (evento) {
    evento.preventDefault();
    limparErros();
    var data = document.getElementById('id_data_consulta').value;
    var hora = document.getElementById('id_hora_consulta').value;
    var tipo = document.getElementById('id_tipo').value;
    var faltando = {};
    if (!select.value) faltando.animal = ['Escolha o tutor/animal nas sugestões.'];
    if (!data || !hora) faltando.data_hora = ['Escolha um dia e um horário livre na agenda.'];
    if (!tipo) faltando.tipo = ['Escolha o tipo de atendimento.'];
    if (Object.keys(faltando).length) { mostrarErros(faltando); return; }

    var textoOriginal = botao.textContent;
    botao.disabled = true;
    botao.textContent = 'Agendando…';
    try {
      mostrarSucesso(await VetAPI.post(form.dataset.urlConsultas, {
        animal: Number(select.value), data_hora: data + 'T' + hora, tipo: tipo,
        observacoes: document.getElementById('id_observacoes').value
      }));
    } catch (erro) {
      if (erro.status === 400) {
        mostrarErros(erro.dados);
        if (erro.dados && erro.dados.data_hora) agenda.recarregar();
      } else if (erro.status === 403) {
        mostrarErros({ geral: ['Sua sessão expirou. Entre novamente para agendar.'] });
      } else {
        mostrarErros({ geral: ['Não foi possível agendar agora. Tente novamente em instantes.'] });
      }
    } finally {
      botao.disabled = false;
      botao.textContent = textoOriginal;
    }
  });
}());
