/*
 * VETSystem — Sistema de Agendamento Veterinário
 * ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
 *
 * Arquivo    : static/js/autocomplete.js
 * Função     : Combobox acessível (WAI-ARIA 1.2) que busca /api/animais/?search=.
 * Fluxograma : etapa 2 — "Sugerir proprietário e animal"
 *
 * Autor      : Lucas Eduardo Rocha (RA 24217901)
 * Data       : 2026-10-13
 */
(function () {
  'use strict';

  function VetAutocomplete(o) {
    this.campo = document.getElementById(o.campoId);
    this.lista = document.getElementById(o.listaId);
    this.status = document.getElementById(o.statusId);
    this.select = document.getElementById(o.selectId);   // <select id_animal> original (reserva sem JS)
    this.url = o.url;
    this.aoFalhar = o.aoFalhar || function () {};
    this.itens = [];
    this.ativo = -1;
    this.temporizador = null;
    this.ultimaBusca = '';
    var self = this;
    this.campo.addEventListener('input', function () {
      self.select.value = '';                             // texto mudou: escolha anterior deixa de valer
      window.clearTimeout(self.temporizador);
      self.temporizador = window.setTimeout(function () { self.buscar(self.campo.value.trim()); }, 250);
    });
    this.campo.addEventListener('keydown', function (e) { self._teclado(e); });
    this.campo.addEventListener('blur', function () { window.setTimeout(function () { self.fechar(); }, 150); });
    this.lista.addEventListener('mousedown', function (e) {
      var opcao = e.target.closest('[role="option"]');
      if (opcao) { e.preventDefault(); self.escolher(Number(opcao.dataset.indice)); }
    });
  }

  VetAutocomplete.prototype.buscar = async function (termo) {
    if (termo.length < 2) { this.fechar(); this._anunciar(''); return; }
    this.ultimaBusca = termo;
    try {
      var dados = await VetAPI.get(this.url + '?search=' + encodeURIComponent(termo) + '&limit=8');
      if (termo !== this.ultimaBusca) return;            // resposta atrasada de uma busca antiga
      this.itens = dados.results || [];
      this._desenhar();
    } catch (erro) {
      this.fechar();
      this._anunciar('Não foi possível buscar agora. Use a lista de animais.');
      this.aoFalhar();
    }
  };

  VetAutocomplete.prototype._desenhar = function () {
    var self = this;
    this.lista.textContent = '';
    this.ativo = -1;
    this.campo.removeAttribute('aria-activedescendant');
    if (!this.itens.length) {
      this.fechar();
      this._anunciar('Nenhum tutor ou animal encontrado. Use "Cadastrar tutor e animal".');
      return;
    }
    this.itens.forEach(function (animal, indice) {
      var li = document.createElement('li');
      li.id = 'sugestao-' + animal.id;
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', 'false');
      li.dataset.indice = String(indice);
      li.className = 'vs-opcao';
      var titulo = document.createElement('span');
      titulo.className = 'font-semibold';
      titulo.textContent = animal.nome + ' (' + animal.especie_display + ')';
      var detalhe = document.createElement('span');
      detalhe.className = 'block text-xs text-gray-600';
      detalhe.textContent = 'Tutor: ' + animal.proprietario_nome + ' · ' + animal.proprietario_telefone;
      li.appendChild(titulo);
      li.appendChild(detalhe);
      self.lista.appendChild(li);
    });
    this.lista.hidden = false;
    this.campo.setAttribute('aria-expanded', 'true');
    this._anunciar(this.itens.length + (this.itens.length === 1 ? ' sugestão.' : ' sugestões.') +
      ' Use as setas para escolher e Enter para confirmar.');
  };

  VetAutocomplete.prototype._teclado = function (e) {
    var aberto = !this.lista.hidden;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!aberto && this.itens.length) { this.lista.hidden = false; this.campo.setAttribute('aria-expanded', 'true'); }
      this._mover(1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      this._mover(-1);
    } else if (e.key === 'Enter' && aberto && this.ativo >= 0) {
      e.preventDefault();
      this.escolher(this.ativo);
    } else if (e.key === 'Escape') {
      if (aberto) { e.preventDefault(); this.fechar(); } else { this.campo.value = ''; this.select.value = ''; }
    }
  };

  VetAutocomplete.prototype._mover = function (passo) {
    if (!this.itens.length || this.lista.hidden) return;
    var opcoes = this.lista.querySelectorAll('[role="option"]');
    if (this.ativo >= 0) opcoes[this.ativo].setAttribute('aria-selected', 'false');
    this.ativo = (this.ativo + passo + this.itens.length) % this.itens.length;
    var atual = opcoes[this.ativo];
    atual.setAttribute('aria-selected', 'true');
    atual.scrollIntoView({ block: 'nearest' });
    this.campo.setAttribute('aria-activedescendant', atual.id);
  };

  VetAutocomplete.prototype.escolher = function (indice) {
    var animal = this.itens[indice];
    if (animal) this.selecionar(animal);
  };

  /* Também usado pelo seletor em modal (seletor_cadastro.js). */
  VetAutocomplete.prototype.selecionar = function (animal) {
    this.select.value = String(animal.id);
    this.campo.value = animal.nome + ' (' + animal.especie_display + ') — ' + animal.proprietario_nome;
    this.campo.removeAttribute('aria-invalid');
    this.fechar();
    this._anunciar('Selecionado: ' + this.campo.value + '.');
  };

  VetAutocomplete.prototype.fechar = function () {
    this.lista.hidden = true;
    this.campo.setAttribute('aria-expanded', 'false');
    this.campo.removeAttribute('aria-activedescendant');
  };

  VetAutocomplete.prototype._anunciar = function (texto) { if (this.status) this.status.textContent = texto; };

  window.VetAutocomplete = VetAutocomplete;
}());
