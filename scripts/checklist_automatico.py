"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : scripts/checklist_automatico.py
Função  : Executa no Chrome (Playwright) os itens dos checklists manuais 5.9 e 6.10
          (docs/metricas/checklist_manual.md) que podem ser conferidos por script: teclado,
          foco visível, menu e rolagem a 375 px, conflito em duas abas, agendamento sem JS
          e mudanças de status. Usa um banco SQLite próprio com os dados de demonstração.
          Os itens que dependem de olho humano (leitor de tela, leitura das mensagens)
          continuam no checklist para o Lucas.
          Uso: .venv/bin/python scripts/checklist_automatico.py  →  imprime a tabela de resultados
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-23
"""
import sys
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent / 'video'))
import gravar_video as gv  # noqa: E402  (reaproveita banco, servidor e usuário do vídeo)

gv.BANCO = gv.SAIDA / 'checklist.sqlite3'
gv.PORTA = 8766
gv.BASE = f'http://127.0.0.1:{gv.PORTA}'
TELAS = ['/', '/dashboard/', '/consultas/', '/consultas/nova/', '/consultas/agenda/',
         '/animais/', '/proprietarios/', '/disponibilidade/']
resultados = []


def item(codigo, descricao, funcao):
    """Executa uma verificação e guarda ✅/❌ com o detalhe."""
    try:
        detalhe = funcao()
        resultados.append((codigo, descricao, '✅', detalhe or ''))
    except Exception as erro:  # noqa: BLE001 — qualquer falha vira ❌ no relatório
        resultados.append((codigo, descricao, '❌', str(erro).splitlines()[0][:120]))


def entrar(pagina):
    pagina.goto(gv.BASE + '/login/')
    pagina.fill('#id_username', gv.USUARIO)
    pagina.fill('#id_password', gv.SENHA)
    pagina.click('button[type=submit]')
    pagina.wait_for_url('**/dashboard/')


def foco(pagina):
    """Descreve o elemento com foco: tag, texto e se o contorno de foco é visível."""
    return pagina.evaluate("""() => {
        const el = document.activeElement, cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return {tag: el.tagName + (el.id ? '#' + el.id : '') + (el.type ? '[' + el.type + ']' : ''), texto: (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().slice(0, 40),
                nativo: !el.matches(':focus'), visivel: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none',
                y: r.top + scrollY, corpo: el === document.body};
    }""")


def sucesso(pagina):
    """Espera o painel "Consulta agendada!"; se não vier, falha com a mensagem de erro da tela."""
    try:
        pagina.locator('#painel-sucesso').wait_for(timeout=8000)
    except Exception:
        erros = pagina.locator('#mensagens-form, [data-erro-campo]').all_inner_texts()
        raise AssertionError('sem sucesso: ' + ' | '.join(e.strip() for e in erros if e.strip())) from None


def escolher_horario(pagina):
    """Escolhe pelo teclado o primeiro dia com horários livres e o primeiro horário."""
    for _ in range(3):
        dias = pagina.locator('#agenda-dias .vs-dia:not([disabled])')
        for i in range(1, dias.count()):
            dias.nth(i).focus()
            pagina.keyboard.press('Enter')
            pagina.wait_for_timeout(700)
            if pagina.locator('#agenda-horarios .vs-slot').count():
                pagina.locator('#agenda-horarios .vs-slot input').first.focus()
                pagina.keyboard.press('Space')
                return pagina.locator('#agenda-horarios .vs-slot').first.inner_text()
        pagina.click('#agenda-proximo')
        pagina.wait_for_timeout(700)
    raise AssertionError('nenhum horário livre em 3 semanas')


def main():
    gv.preparar_banco(False)
    servidor = gv.subir_servidor()
    try:
        with sync_playwright() as pw:
            navegador = pw.chromium.launch(channel='chrome')
            ctx = navegador.new_context(viewport={'width': 1280, 'height': 900})
            p = ctx.new_page()
            entrar(p)

            # ---------------- Fase 5 (5.9) — teclado e celular ----------------
            def pular():
                p.goto(gv.BASE + '/dashboard/')
                p.keyboard.press('Tab')
                f = foco(p)
                assert 'Pular' in f['texto'], f"1º Tab foi para {f['tag']} '{f['texto']}'"
                p.keyboard.press('Enter')
                alvo = p.evaluate('document.activeElement.id')
                assert alvo == 'conteudo', f'foco foi para #{alvo}'
                return '1º Tab = "Pular para o conteúdo"; Enter leva o foco a #conteudo'
            item('5.1', 'Link "Pular para o conteúdo"', pular)

            def percorrer(tela, passos=60):
                p.goto(gv.BASE + tela)
                vistos = []
                for _ in range(passos):
                    p.keyboard.press('Tab')
                    f = foco(p)
                    if f['corpo']:
                        break
                    vistos.append(f)
                return vistos

            def foco_visivel():
                sem, nativos = [], 0
                for tela in TELAS:
                    vistos = percorrer(tela)
                    nativos += sum(v['nativo'] for v in vistos)
                    sem += [f"{tela} {v['tag']} '{v['texto']}'" for v in vistos if not v['visivel'] and not v['nativo']]
                assert not sem, f'{len(sem)} sem contorno: ' + '; '.join(sem[:3])
                return (f'contorno de foco em todos os elementos de {len(TELAS)} telas'
                        f' ({nativos} paradas no ícone de calendário do campo de data, controle do próprio navegador)')
            item('5.2', 'Foco sempre visível', foco_visivel)

            def ordem():
                positivos = 0
                for tela in TELAS:
                    p.goto(gv.BASE + tela)
                    positivos += p.locator('[tabindex]:not([tabindex="0"]):not([tabindex="-1"])').count()
                assert positivos == 0, f'{positivos} elementos com tabindex positivo'
                return 'nenhum tabindex positivo: a ordem do Tab é a do código (menu → conteúdo → rodapé)'
            item('5.3', 'Ordem do Tab segue a ordem visual', ordem)

            def sem_armadilha():
                for tela in TELAS:
                    p.goto(gv.BASE + tela)
                    ida = [foco(p)['texto'] for _ in range(6) if not p.keyboard.press('Tab')]
                    volta = [foco(p)['texto'] for _ in range(5) if not p.keyboard.press('Shift+Tab')]
                    assert volta == ida[-2::-1], f'{tela}: Shift+Tab não refaz o caminho'
                return f'Shift+Tab refaz o caminho do Tab em {len(TELAS)} telas, sem prender o foco'
            item('5.4', 'Shift+Tab sem armadilhas de foco', sem_armadilha)

            def erro_ligado():
                p.goto(gv.BASE + '/proprietarios/novo/')
                p.evaluate("document.querySelector('#conteudo form').noValidate = true")  # testa o servidor, não o 'required' do navegador
                p.locator('#conteudo form [type=submit]').last.focus()
                with p.expect_navigation():
                    p.keyboard.press('Enter')
                ligados = p.evaluate("""() => [...document.querySelectorAll('[aria-invalid="true"]')].filter(c =>
                    (c.getAttribute('aria-describedby') || '').split(' ').some(id => {
                        const e = document.getElementById(id); return e && e.innerText.trim(); })).length""")
                assert ligados > 0, 'nenhum campo com erro ligado por aria-describedby'
                return f'formulário enviado pelo teclado; {ligados} campos com erro ligado (aria-invalid + aria-describedby)'
            item('5.6', 'Erro de validação ligado ao campo', erro_ligado)

            def sair():
                f = [v for v in percorrer('/dashboard/') if v['texto'] == 'Sair']
                assert f, '"Sair" não é alcançado pelo Tab'
                return '"Sair" alcançado pelo Tab'
            item('5.10', 'Sair acionável pelo teclado', sair)

            celular = navegador.new_context(viewport={'width': 375, 'height': 812}, is_mobile=True, has_touch=True)
            c = celular.new_page()
            entrar(c)

            def menu():
                c.goto(gv.BASE + '/dashboard/')
                c.focus('#botao-menu')
                c.keyboard.press('Enter')
                assert c.get_attribute('#botao-menu', 'aria-expanded') == 'true', 'aria-expanded não mudou'
                links = c.locator('#menu-movel a:visible').count()
                assert links > 0, 'menu aberto sem links visíveis'
                c.keyboard.press('Enter')
                assert c.get_attribute('#botao-menu', 'aria-expanded') == 'false', 'não fechou'
                return f'abre e fecha pelo teclado (aria-expanded true/false); {links} links visíveis'
            item('5.8', 'Menu no celular (375 px)', menu)

            def sem_rolagem():
                largas = []
                for tela in TELAS:
                    c.goto(gv.BASE + tela)
                    w = c.evaluate('document.documentElement.scrollWidth')
                    if w > 375:
                        culpado = c.evaluate('''() => { const l = [...document.querySelectorAll('#conteudo *')]
                            .filter(e => e.getBoundingClientRect().right > 380 && !e.closest('.overflow-x-auto'));
                            const e = l[0]; return e ? e.tagName + '.' + [...e.classList].slice(0, 3).join('.') : '?'; }''')
                        largas.append(f'{tela} ({w}px, {culpado})')
                assert not largas, 'rolagem horizontal: ' + ', '.join(largas)
                return f'{len(TELAS)} telas sem rolagem horizontal a 375 px'
            item('5.9', 'Sem rolagem horizontal a 375 px', sem_rolagem)
            celular.close()

            # ---------------- Fase 6 (6.10) — JavaScript do agendamento ----------------
            def agendar_teclado():
                p.goto(gv.BASE + '/consultas/nova/')
                p.focus('#campo-busca')
                p.keyboard.type('Me', delay=60)
                p.locator('#lista-sugestoes li').first.wait_for()
                p.keyboard.press('ArrowDown')
                p.keyboard.press('Enter')
                hora = escolher_horario(p)
                p.focus('#id_tipo')
                p.keyboard.press('ArrowDown')
                p.focus('#btn-agendar')
                p.keyboard.press('Enter')
                sucesso(p)
                return f'busca → setas → Enter → dia/horário ({hora}) → Enter: "Consulta agendada!"'
            item('6.1', 'Agendar só com o teclado', agendar_teclado)

            def conflito():
                abas = [p, ctx.new_page()]
                for aba in abas:
                    aba.goto(gv.BASE + '/consultas/nova/')
                    aba.fill('#campo-busca', 'Bo')
                    aba.locator('#lista-sugestoes li').first.click()
                for aba in abas:
                    escolher_horario(aba)
                    aba.select_option('#id_tipo', index=1)
                abas[0].click('#btn-agendar')
                sucesso(abas[0])
                abas[1].click('#btn-agendar')
                abas[1].wait_for_timeout(1500)
                assert abas[1].locator('#painel-sucesso').is_hidden(), 'a 2ª aba também agendou'
                msg = abas[1].locator('[role=alert]:visible, .text-red-700:visible').first.inner_text()
                abas[1].close()
                return f'2ª aba recusada: "{msg.strip()[:70]}"'
            item('6.2', 'Conflito em duas abas', conflito)

            def sem_js():
                nojs = navegador.new_context(java_script_enabled=False)
                n = nojs.new_page()
                entrar(n)
                n.goto(gv.BASE + '/consultas/nova/')
                n.select_option('#id_animal', index=1)
                dia = date.today() + timedelta(days=1)
                while dia.weekday() >= 5:
                    dia += timedelta(days=1)
                n.fill('#id_data_consulta', dia.isoformat())
                if n.evaluate("document.getElementById('id_hora_consulta').tagName") == 'SELECT':
                    n.select_option('#id_hora_consulta', '15:30')
                else:
                    n.fill('#id_hora_consulta', '15:30')
                n.select_option('#id_tipo', index=1)
                n.locator('#conteudo form [type=submit]').last.click()
                n.wait_for_load_state()
                url = n.url
                nojs.close()
                assert '/consultas/nova/' not in url, 'o formulário não foi aceito'
                return f'formulário simples aceito sem JavaScript ({dia:%d/%m} 15:30) → {url.replace(gv.BASE, "")}'
            item('6.3', 'Agendar com JavaScript desativado', sem_js)

            def whatsapp():
                p.goto(gv.BASE + '/dashboard/')
                botao = p.locator('a.btn-acao-whatsapp:visible').first
                with ctx.expect_page() as nova:
                    botao.click()
                url = nova.value.url
                nova.value.close()
                assert 'wa.me' in url or 'whatsapp' in url, f'abriu {url}'
                p.wait_for_timeout(1000)
                assert p.get_by_text('Confirmado').first.is_visible(), 'selo não virou "Confirmado"'
                return 'abre wa.me com a mensagem e o selo vira "Confirmado"'
            item('6.4', 'Confirmar pelo WhatsApp', whatsapp)

            def status():
                p.goto(gv.BASE + '/dashboard/')
                for acao in ('realizado', 'cancelado'):
                    antes = p.locator(f'[data-acao-status="{acao}"]:visible').count()
                    p.locator(f'[data-acao-status="{acao}"]:visible').first.click()
                    p.wait_for_timeout(1000)
                    assert p.locator(f'[data-acao-status="{acao}"]:visible').count() < antes, f'{acao}: nada mudou'
                return '"Atendimento realizado" e "Registrar ausência" atualizam sem recarregar'
            item('6.5', 'Status no dashboard', status)
            navegador.close()
    finally:
        servidor.terminate()

    print(f'\nChecklist automático — {date.today():%d/%m/%Y} — Chrome (Playwright)\n')
    print('| Item | Verificação | Resultado | Detalhe |\n|---|---|---|---|')
    for linha in resultados:
        print('| ' + ' | '.join(linha) + ' |')
    return 0 if all(r[2] == '✅' for r in resultados) else 1


if __name__ == '__main__':
    sys.exit(main())
