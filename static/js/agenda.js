/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/agenda.js
 * Função     : Agenda de 7 dias por vez + horários livres (rádios) via /api/horarios-livres/.
 * Fluxograma : etapas 3 e 4 — "Consultar horários livres" e "Exibir agenda interativa"
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-13
 */
(function () {
  'use strict';
  var SEMANAS_A_FRENTE = 8;

  function formatar(d) { return String(d.getDate()).padStart(2, '0') + '/' + String(d.getMonth() + 1).padStart(2, '0'); }

  function VetAgenda(o) {
    this.dias = document.getElementById(o.diasId);
    this.horarios = document.getElementById(o.horariosId);       // <fieldset>
    this.status = document.getElementById(o.statusId);
    this.titulo = document.getElementById(o.tituloId);
    this.btnAnterior = document.getElementById(o.anteriorId);
    this.btnProximo = document.getElementById(o.proximoId);
    this.campoData = document.getElementById(o.campoDataId);     // id_data_consulta (reserva sem JS)
    this.campoHora = document.getElementById(o.campoHoraId);     // id_hora_consulta
    this.urlHorarios = o.urlHorarios;
    this.urlDisponibilidades = o.urlDisponibilidades;
    this.ignorar = o.ignorarId || '';
    this.diasAbertos = new Set();                                // dias da semana do JS (0 = domingo)
    this.hoje = new Date(); this.hoje.setHours(0, 0, 0, 0);
    this.inicio = new Date(this.hoje);
    this.selecionada = null;
    this.selecionouHorario = false;
    var self = this;
    this.btnAnterior.addEventListener('click', function () { self._mudarSemana(-7); });
    this.btnProximo.addEventListener('click', function () { self._mudarSemana(7); });
  }

  VetAgenda.prototype.iniciar = async function () {
    var self = this;
    try {
      var disponibilidades = await VetAPI.get(this.urlDisponibilidades);
      disponibilidades.forEach(function (d) { if (d.ativo) self.diasAbertos.add((d.dia_da_semana + 1) % 7); });
    } catch (erro) {
      return false;                                              // o formulário volta aos campos de reserva
    }
    var inicial = null;
    if (this.campoData.value) {                                  // edição: começa no dia já marcado
      var marcada = VetAPI.dataDeIso(this.campoData.value);
      if (marcada >= this.hoje) inicial = marcada;
    }
    if (!inicial) inicial = this._proximoDiaAberto(this.hoje);
    if (inicial) this.inicio = new Date(inicial);
    this._desenharDias();
    if (inicial) await this.selecionarDia(VetAPI.dataIso(inicial), this.campoHora.value.slice(0, 5));
    return true;
  };

  VetAgenda.prototype._proximoDiaAberto = function (aPartirDe) {
    for (var i = 0; i < SEMANAS_A_FRENTE * 7; i++) {
      var dia = new Date(aPartirDe); dia.setDate(dia.getDate() + i);
      if (this.diasAbertos.has(dia.getDay())) return dia;
    }
    return null;
  };

  VetAgenda.prototype._mudarSemana = function (deslocamento) {
    var novo = new Date(this.inicio); novo.setDate(novo.getDate() + deslocamento);
    var limite = new Date(this.hoje); limite.setDate(limite.getDate() + (SEMANAS_A_FRENTE - 1) * 7);
    if (novo < this.hoje) novo = new Date(this.hoje);
    if (novo > limite) return;
    this.inicio = novo;
    this._desenharDias();
    this._status('Mostrando ' + this.titulo.textContent + '. Escolha um dia.');
  };

  VetAgenda.prototype._desenharDias = function () {
    var self = this;
    this.dias.textContent = '';
    var fim = new Date(this.inicio); fim.setDate(fim.getDate() + 6);
    this.titulo.textContent = 'dias de ' + formatar(this.inicio) + ' a ' + formatar(fim);
    for (var i = 0; i < 7; i++) {
      var dia = new Date(this.inicio); dia.setDate(dia.getDate() + i);
      var iso = VetAPI.dataIso(dia);
      var aberto = this.diasAbertos.has(dia.getDay());
      var botao = document.createElement('button');
      botao.type = 'button';
      botao.className = 'vs-dia';
      botao.dataset.data = iso;
      botao.setAttribute('aria-pressed', iso === this.selecionada ? 'true' : 'false');
      botao.setAttribute('aria-label', VetAPI.dataPorExtenso(dia) + (aberto ? '' : ' — clínica fechada'));
      [VetAPI.DIAS_CURTOS[dia.getDay()], formatar(dia), aberto ? '' : 'fechado'].forEach(function (texto, n) {
        if (!texto) return;
        var parte = document.createElement('span');
        parte.className = n === 1 ? 'block font-bold' : 'block text-xs';
        parte.textContent = texto;
        botao.appendChild(parte);
      });
      botao.disabled = !aberto;
      botao.addEventListener('click', function (e) { self.selecionarDia(e.currentTarget.dataset.data); });
      this.dias.appendChild(botao);
    }
    this.btnAnterior.disabled = this.inicio <= this.hoje;
    var limite = new Date(this.hoje); limite.setDate(limite.getDate() + (SEMANAS_A_FRENTE - 1) * 7);
    this.btnProximo.disabled = this.inicio >= limite;
  };

  VetAgenda.prototype.selecionarDia = async function (iso, horaMarcada) {
    if (this.selecionouHorario) {                                 // trocou de dia: limpa a escolha anterior
      this.campoData.value = ''; this.campoHora.value = ''; this.selecionouHorario = false;
    }
    this.selecionada = iso;
    this.dias.querySelectorAll('.vs-dia').forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.data === iso ? 'true' : 'false');
    });
    var extenso = VetAPI.dataPorExtenso(VetAPI.dataDeIso(iso));
    this.horarios.setAttribute('aria-busy', 'true');
    this.horarios.classList.add('opacity-50');                   // mantém o desenho anterior enquanto carrega
    this._status('Consultando horários livres de ' + extenso + '…');
    try {
      var url = this.urlHorarios + '?data=' + iso + (this.ignorar ? '&ignorar=' + this.ignorar : '');
      var resposta = await VetAPI.get(url);
      if (this.selecionada !== iso) return;                       // o usuário já clicou em outro dia
      this._desenharHorarios(resposta, extenso, horaMarcada);
    } catch (erro) {
      this._status('Não foi possível consultar os horários. Tente novamente.');
    } finally {
      this.horarios.removeAttribute('aria-busy');
      this.horarios.classList.remove('opacity-50');
    }
  };

  VetAgenda.prototype._desenharHorarios = function (resposta, extenso, horaMarcada) {
    var self = this;
    this.horarios.textContent = '';
    var legenda = document.createElement('legend');
    legenda.className = 'text-sm font-semibold text-gray-700 mb-2';
    legenda.textContent = 'Horários livres — ' + extenso +
      (resposta.aberto ? ' (expediente ' + resposta.inicio + ' às ' + resposta.fim + ')' : '');
    this.horarios.appendChild(legenda);
    var horarios = resposta.horarios.slice();
    var mesmoDia = this.campoData.value === resposta.data;
    if (horaMarcada && mesmoDia && horarios.indexOf(horaMarcada) === -1) { horarios.push(horaMarcada); horarios.sort(); }
    if (!horarios.length) {                                       // decisão "Horário disponível? Não"
      this._status(resposta.aberto ? 'Nenhum horário livre em ' + extenso + '. Escolha outro dia.'
                                   : 'A clínica não atende em ' + extenso + '. Escolha outro dia.');
      return;
    }
    var grade = document.createElement('div');
    grade.className = 'flex flex-wrap gap-2';
    horarios.forEach(function (hora) {
      var rotulo = document.createElement('label');
      rotulo.className = 'vs-slot';
      var radio = document.createElement('input');
      radio.type = 'radio';
      radio.name = 'horario_agenda';
      radio.value = hora;
      radio.checked = mesmoDia && hora === horaMarcada;
      radio.addEventListener('change', function () {
        self.campoData.value = resposta.data;
        self.campoHora.value = hora;
        self.selecionouHorario = true;
        self._status('Horário escolhido: ' + extenso + ' às ' + hora + '.');
      });
      var texto = document.createElement('span');
      texto.textContent = hora;
      rotulo.appendChild(radio);
      rotulo.appendChild(texto);
      grade.appendChild(rotulo);
    });
    this.horarios.appendChild(grade);
    this._status(horarios.length + (horarios.length === 1 ? ' horário livre' : ' horários livres') + ' em ' + extenso + '.');
  };

  VetAgenda.prototype.recarregar = function () {                 // após conflito: "Não" → volta à agenda
    if (!this.selecionada) return;
    this.campoData.value = ''; this.campoHora.value = ''; this.selecionouHorario = false;
    return this.selecionarDia(this.selecionada);
  };

  VetAgenda.prototype._status = function (texto) { this.status.textContent = texto; };

  window.VetAgenda = VetAgenda;
}());
