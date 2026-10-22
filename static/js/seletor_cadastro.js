/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/seletor_cadastro.js
 * Função     : Modal com abas (Tutor/Animal) para seleção de pacientes cadastrados.
 * Fluxograma : etapa 2 — "Sugerir proprietário e animal"
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-13
 */
(function () {
  'use strict';

  function textoAnimal(animal) {
    var partes = ['Tutor: ' + animal.proprietario_nome];
    if (animal.raca) partes.push(animal.raca);
    if (animal.peso) partes.push(String(animal.peso).replace('.', ',') + ' kg');
    return partes.join(' · ');
  }

  function resumo(dados, singular, plural) {
    var total = dados.count, mostrados = dados.results.length;
    if (!total) return 'Nenhum ' + singular + ' encontrado.';
    var texto = total + ' ' + (total === 1 ? singular + ' encontrado' : plural + ' encontrados') + '.';
    if (mostrados < total) texto += ' Mostrando os ' + mostrados + ' primeiros; refine o filtro.';
    return texto;
  }

  /* Item de lista = botão (Tab/Enter/Espaço funcionam sem código extra). Dados da API só via textContent. */
  function item(titulo, detalhe, aoClicar) {
    var li = document.createElement('li');
    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'vs-item';
    var t = document.createElement('span');
    t.className = 'font-semibold';
    t.textContent = titulo;
    var d = document.createElement('span');
    d.className = 'block text-xs text-gray-600';
    d.textContent = detalhe;
    botao.appendChild(t);
    botao.appendChild(d);
    botao.addEventListener('click', aoClicar);
    li.appendChild(botao);
    return li;
  }

  function VetSeletor(o) {
    this.dialogo = document.getElementById(o.dialogoId);
    this.abridor = document.getElementById(o.abridorId);
    this.urlTutores = o.urlTutores;
    this.urlAnimais = o.urlAnimais;
    this.urlNovoAnimal = o.urlNovoAnimal;   // animal-create?fluxo=agendamento
    this.aoEscolher = o.aoEscolher;
    this.versoes = {};
    this.temporizadores = {};
    if (!this.dialogo || typeof this.dialogo.showModal !== 'function') return;   // sem <dialog>: fica só a busca rápida
    this.abas = Array.prototype.slice.call(this.dialogo.querySelectorAll('[role="tab"]'));
    var self = this;
    this.abridor.hidden = false;
    this.abridor.addEventListener('click', function () { self.abrir(); });
    this.dialogo.querySelectorAll('[data-fechar-dialogo]').forEach(function (b) {
      b.addEventListener('click', function () { self.dialogo.close(); });
    });
    this.dialogo.addEventListener('click', function (e) { if (e.target === self.dialogo) self.dialogo.close(); });  // clique no fundo
    this.dialogo.addEventListener('close', function () { self.abridor.focus(); });   // Esc também cai aqui
    this.abas.forEach(function (aba) {
      aba.addEventListener('click', function () { self.mostrarAba(aba); });
      aba.addEventListener('keydown', function (e) { self._tecladoAbas(e, aba); });
    });
    this._aoDigitar('filtro-tutor', function () { self.buscarTutores(); });
    this._aoDigitar('filtro-animal', function () { self.buscarAnimais(); });
    document.getElementById('filtro-especie').addEventListener('change', function () { self.buscarAnimais(); });
  }

  VetSeletor.prototype._aoDigitar = function (id, buscar) {
    var self = this;
    document.getElementById(id).addEventListener('input', function () {
      window.clearTimeout(self.temporizadores[id]);
      self.temporizadores[id] = window.setTimeout(buscar, 250);
    });
  };

  VetSeletor.prototype.abrir = function () {
    this.dialogo.showModal();
    this.mostrarAba(this.abas[0]);
    document.getElementById('filtro-tutor').focus();
  };

  /* Abas WAI-ARIA com ativação automática: setas, Home e End trocam de aba. */
  VetSeletor.prototype.mostrarAba = function (escolhida) {
    this.abas.forEach(function (aba) {
      var ativa = aba === escolhida;
      aba.setAttribute('aria-selected', String(ativa));
      aba.tabIndex = ativa ? 0 : -1;
      document.getElementById(aba.getAttribute('aria-controls')).hidden = !ativa;
    });
    if (escolhida.id === 'aba-tutor') this.buscarTutores(); else this.buscarAnimais();
  };

  VetSeletor.prototype._tecladoAbas = function (e, aba) {
    var i = this.abas.indexOf(aba), n = this.abas.length, destino = null;
    if (e.key === 'ArrowRight') destino = this.abas[(i + 1) % n];
    else if (e.key === 'ArrowLeft') destino = this.abas[(i - 1 + n) % n];
    else if (e.key === 'Home') destino = this.abas[0];
    else if (e.key === 'End') destino = this.abas[n - 1];
    if (!destino) return;
    e.preventDefault();
    this.mostrarAba(destino);
    destino.focus();
  };

  /* GET com controle de versão: uma resposta atrasada não sobrescreve a busca mais nova. */
  VetSeletor.prototype._buscar = async function (chave, url, statusId) {
    var versao = (this.versoes[chave] || 0) + 1;
    this.versoes[chave] = versao;
    var status = document.getElementById(statusId);
    status.textContent = 'Buscando…';
    try {
      var dados = await VetAPI.get(url);
      return versao === this.versoes[chave] ? dados : null;
    } catch (erro) {
      if (versao === this.versoes[chave]) status.textContent = 'Não foi possível buscar agora. Tente novamente.';
      return null;
    }
  };

  VetSeletor.prototype.buscarTutores = async function () {
    var termo = document.getElementById('filtro-tutor').value.trim();
    document.getElementById('animais-do-tutor').hidden = true;
    var dados = await this._buscar('tutor',
      this.urlTutores + '?search=' + encodeURIComponent(termo) + '&limit=20', 'status-tutor');
    if (!dados) return;
    var self = this, lista = document.getElementById('lista-tutores');
    lista.textContent = '';
    dados.results.forEach(function (tutor) {
      var animais = tutor.total_animais + (tutor.total_animais === 1 ? ' animal' : ' animais');
      lista.appendChild(item(tutor.nome, tutor.telefone + ' · ' + animais,
        function () { self.mostrarAnimaisDoTutor(tutor); }));
    });
    document.getElementById('status-tutor').textContent = resumo(dados, 'tutor', 'tutores');
  };

  VetSeletor.prototype.mostrarAnimaisDoTutor = async function (tutor) {
    var dados = await this._buscar('tutor', this.urlAnimais + '?proprietario=' + tutor.id + '&limit=50', 'status-tutor');
    if (!dados) return;
    var self = this, lista = document.getElementById('lista-animais-tutor');
    var titulo = document.getElementById('titulo-animais-tutor');
    lista.textContent = '';
    dados.results.forEach(function (animal) {
      lista.appendChild(item(animal.nome + ' (' + animal.especie_display + ')', textoAnimal(animal),
        function () { self.escolher(animal); }));
    });
    titulo.textContent = 'Animais de ' + tutor.nome + ' (' + dados.count + ')';
    document.getElementById('link-novo-animal').href = this.urlNovoAnimal + '&proprietario=' + tutor.id;
    document.getElementById('status-tutor').textContent =
      dados.count ? 'Escolha o animal.' : 'Este tutor ainda não tem animal cadastrado.';
    document.getElementById('animais-do-tutor').hidden = false;
    titulo.focus();
  };

  VetSeletor.prototype.buscarAnimais = async function () {
    var termo = document.getElementById('filtro-animal').value.trim();
    var especie = document.getElementById('filtro-especie').value;
    var url = this.urlAnimais + '?search=' + encodeURIComponent(termo) + '&limit=20' +
      (especie ? '&especie=' + encodeURIComponent(especie) : '');
    var dados = await this._buscar('animal', url, 'status-animal');
    if (!dados) return;
    var self = this, lista = document.getElementById('lista-animais');
    lista.textContent = '';
    dados.results.forEach(function (animal) {
      lista.appendChild(item(animal.nome + ' (' + animal.especie_display + ')', textoAnimal(animal),
        function () { self.escolher(animal); }));
    });
    document.getElementById('status-animal').textContent = resumo(dados, 'animal', 'animais');
  };

  VetSeletor.prototype.escolher = function (animal) {
    this.dialogo.close();        // fecha antes: com o modal aberto, o resto da página fica inerte
    this.aoEscolher(animal);
  };

  window.VetSeletor = VetSeletor;
}());
