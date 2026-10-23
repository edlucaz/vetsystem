"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : scripts/video/gravar_video.py
Função  : Grava (ou apresenta ao vivo) o vídeo da parte técnica: percorre as telas na ordem do
          fluxograma v3 e destaca, ao lado, a etapa do fluxograma e as entidades/relacionamentos
          do DER que aparecem em cada cena (palco.html).
          Usa um banco SQLite próprio (video_saida/video.sqlite3) com dados de demonstração;
          não toca no banco de desenvolvimento nem no de produção.
          Uso:
            .venv/bin/python scripts/video/gravar_video.py               # grava cenas em video_saida/
            .venv/bin/python scripts/video/gravar_video.py --ao-vivo     # janela aberta, Enter avança (OBS)
            opções: --sem-camera  --ritmo 1.3 (mais lento)  --cenas 3,4  --manter-banco
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-23
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
SAIDA = RAIZ / 'video_saida'
BANCO = SAIDA / 'video.sqlite3'
PORTA = 8765
BASE = f'http://127.0.0.1:{PORTA}'
PYTHON = str(RAIZ / '.venv' / 'bin' / 'python')
USUARIO, SENHA = 'fernanda', 'ativopet2026'

# Cursor visível dentro do sistema (o Chrome automatizado não desenha o ponteiro)
CURSOR_JS = """
if (window.top !== window) {
  addEventListener('DOMContentLoaded', function () {
    var c = document.createElement('div');
    c.style.cssText = 'position:fixed;z-index:2147483647;width:22px;height:22px;margin:-11px 0 0 -11px;' +
      'border-radius:50%;background:rgba(185,71,26,.35);border:2px solid #B9471A;pointer-events:none;' +
      'transition:transform .15s;left:-50px;top:-50px';
    document.body.appendChild(c);
    addEventListener('mousemove', function (e) { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
    addEventListener('mousedown', function () { c.style.transform = 'scale(.6)'; }, true);
    addEventListener('mouseup', function () { c.style.transform = 'scale(1)'; }, true);
  });
}
"""

# Dados extras criados depois do popular_demo: usuária da clínica e duas consultas hoje
PREPARO_ORM = f"""
import json
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from agendamentos.models import Animal, Consulta
u, _ = User.objects.get_or_create(username='{USUARIO}', defaults={{'first_name': 'Fernanda', 'is_staff': True}})
u.set_password('{SENHA}'); u.save()
agora = timezone.localtime().replace(minute=0, second=0, microsecond=0)
tipo = Consulta.TIPO_CHOICES[0][0]
for i, nome in enumerate(['Mel', 'Bob']):
    Consulta.objects.create(animal=Animal.objects.filter(nome=nome).first(), tipo=tipo,
                            data_hora=agora.replace(hour=8) + timedelta(minutes=17 * (i + 1)),
                            observacoes='Retorno (vídeo)')
print(json.dumps({{'thor': Animal.objects.filter(nome='Thor').first().pk}}))
"""


def ambiente():
    env = dict(os.environ, DATABASE_URL=f'sqlite:///{BANCO}', DEBUG='True',
               DJANGO_SETTINGS_MODULE='settings_video',
               PYTHONPATH=os.pathsep.join([str(AQUI), str(RAIZ)]))
    return env


def manage(*args):
    return subprocess.run([PYTHON, 'manage.py', *args], cwd=RAIZ, env=ambiente(),
                          check=True, capture_output=True, text=True).stdout


def preparar_banco(manter):
    SAIDA.mkdir(exist_ok=True)
    ids_arquivo = SAIDA / 'ids.json'
    if manter and BANCO.exists() and ids_arquivo.exists():
        return json.loads(ids_arquivo.read_text())
    BANCO.unlink(missing_ok=True)
    print('Preparando banco do vídeo…')
    manage('migrate', '--noinput')
    manage('criar_horarios_padrao')
    manage('popular_demo')
    ids = json.loads(manage('shell', '-c', PREPARO_ORM).strip().splitlines()[-1])
    ids_arquivo.write_text(json.dumps(ids))
    return ids


def subir_servidor():
    servidor = subprocess.Popen([PYTHON, 'manage.py', 'runserver', f'127.0.0.1:{PORTA}', '--noreload'],
                                cwd=RAIZ, env=ambiente(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen(BASE + '/', timeout=1)
            return servidor
        except OSError:
            time.sleep(0.5)
    servidor.kill()
    sys.exit('O servidor de vídeo não respondeu na porta %d.' % PORTA)


def html_palco():
    diagramas = RAIZ / 'docs' / 'diagramas'
    return ((AQUI / 'palco.html').read_text(encoding='utf-8')
            .replace('{{FLUXO}}', (diagramas / 'fluxograma_v3.svg').read_text(encoding='utf-8'))
            .replace('{{DER}}', (diagramas / 'der_v3.svg').read_text(encoding='utf-8')))


class Video:
    """Ações com ritmo de apresentação: mouse visível, digitação lenta e pausas."""

    def __init__(self, page, ritmo, ids):
        self.page, self.ritmo, self.ids = page, ritmo, ids
        self.app = page.frame(name='app')

    def pausa(self, segundos=1.5):
        self.page.wait_for_timeout(int(segundos * 1000 * self.ritmo))

    def passo(self, legenda=None, flx=None, der=None, **extra):
        dados = dict(extra)
        if legenda is not None:
            dados['legenda'] = legenda
        if flx is not None:
            dados['flx'] = ['flx-' + i for i in flx]
        if der is not None:
            dados['der'] = ['der-' + i for i in der]
        self.page.evaluate('d => window.palco(d)', dados)

    def ir(self, caminho):
        self.app.goto(BASE + caminho)
        self.app.wait_for_load_state('networkidle')
        self.pausa(1)

    def esperar_url(self, padrao):
        self.app.wait_for_url(re.compile(padrao))
        self.app.wait_for_load_state('networkidle')

    def _alvo(self, alvo):
        return self.app.locator(alvo).first if isinstance(alvo, str) else alvo

    def apontar(self, alvo):
        loc = self._alvo(alvo)
        loc.scroll_into_view_if_needed()
        caixa = loc.bounding_box()
        self.page.mouse.move(caixa['x'] + caixa['width'] / 2, caixa['y'] + caixa['height'] / 2, steps=25)
        self.pausa(0.4)
        return loc

    def clicar(self, alvo):
        self.apontar(alvo).click()
        self.pausa(0.8)

    def digitar(self, alvo, texto):
        loc = self.apontar(alvo)
        loc.click()
        loc.fill('')
        loc.press_sequentially(texto, delay=int(85 * self.ritmo))
        self.pausa(0.6)

    def rolar(self, alvo):
        self._alvo(alvo).evaluate("e => e.scrollIntoView({behavior: 'smooth', block: 'start'})")
        self.pausa(1.2)

    def escolher_dia(self):
        """Clica no primeiro dia (a partir de amanhã) que tenha horários livres."""
        dias = self.app.locator('#agenda-dias .vs-dia:not([disabled])')
        for i in range(1, dias.count()):
            self.clicar(dias.nth(i))
            self.app.wait_for_timeout(800)
            if self.app.locator('#agenda-horarios .vs-slot').count():
                return
        self.clicar('#agenda-proximo')
        self.escolher_dia()


# ----------------------------------------------------------------------------------------------
# Cenas, na ordem do fluxograma. Cada uma: (título, etapas do fluxograma, elementos do DER, função)
# ----------------------------------------------------------------------------------------------
def cena_publica(v):
    v.ir('/')
    v.pausa(2)
    v.rolar('#horarios')
    v.passo('O tutor vê os próximos horários livres (API pública, sem login) e chama a clínica no WhatsApp.')
    v.pausa(2)
    v.apontar('#horarios a[href*="wa.me"], #horarios a')
    v.pausa(2)


def cena_login(v):
    v.ir('/login/')
    v.digitar('#id_username', USUARIO)
    v.digitar('#id_password', SENHA)
    v.clicar('button[type=submit]')
    v.esperar_url(r'/dashboard/')
    v.passo('Login por sessão do Django; a mesma sessão autentica a API REST (com proteção CSRF).')
    v.pausa(3)


def cena_busca(v):
    v.ir('/consultas/nova/')
    v.digitar('#campo-busca', 'Th')
    v.app.locator('#lista-sugestoes li').first.wait_for()
    v.passo('Autocomplete: sugestões de tutor e animal vindas da API enquanto digita.')
    v.pausa(2.5)
    v.app.locator('#campo-busca').fill('')
    v.clicar('#abrir-seletor')
    v.passo('Ou a lista completa em uma janela com abas (Tutor / Animal) e filtros.')
    v.digitar('#filtro-tutor', 'Ana')
    v.pausa(1.5)
    v.clicar('#aba-animal')
    v.pausa(2)
    v.page.keyboard.press('Escape')
    v.pausa(1)


def cena_cadastro(v):
    v.digitar('#campo-busca', 'Juliana')
    v.passo('Cadastrado? Não: nenhum resultado. O cadastro acontece sem sair do agendamento.')
    v.pausa(2)
    v.clicar(v.app.get_by_role('link', name='Cadastrar tutor e animal'))
    v.esperar_url(r'/proprietarios/novo/')
    v.passo('Etapa 1: dados do tutor (Proprietário).', der=['proprietario'])
    v.digitar('#id_nome', 'Juliana Martins')
    v.digitar('#id_telefone', '(19) 99876-5432')
    v.digitar('#id_email', 'juliana.martins@exemplo.com')
    v.clicar('#conteudo [type=submit]')
    v.esperar_url(r'/animais/novo/')
    v.passo('Etapa 2: o animal já vem ligado ao tutor (Proprietário 1:N Animal — "possui").',
            der=['proprietario', 'possui', 'animal'])
    v.pausa(1.5)
    v.digitar('#id_nome', 'Paçoca')
    v.app.select_option('#id_especie', 'cao')
    v.digitar('#id_raca', 'SRD')
    v.digitar('#id_peso', '8,4')
    v.digitar('#id_queixa', 'Vacinação anual')
    v.clicar('#conteudo [type=submit]')
    v.esperar_url(r'/consultas/nova/')
    v.pausa(1.5)


def cena_agenda(v):
    v.passo('Etapa 3: a agenda mostra só os horários livres (/api/horarios-livres/: consultas × Disponibilidade).')
    v.pausa(2)
    v.escolher_dia()
    v.pausa(2.5)


def cena_conflito(v):
    v.clicar('#agenda-horarios .vs-slot')
    v.app.select_option('#id_tipo', index=1)
    v.passo('Enquanto isso, outra pessoa agenda o Thor exatamente neste horário…')
    v.app.evaluate("""async (thor) => {
        const f = document.getElementById('form-consulta');
        const tipo = [...document.getElementById('id_tipo').options].find(o => o.value).value;
        await VetAPI.post(f.dataset.urlConsultas, {animal: thor, tipo: tipo, observacoes: '',
            data_hora: document.getElementById('id_data_consulta').value + 'T' +
                       document.getElementById('id_hora_consulta').value});
    }""", v.ids['thor'])
    v.pausa(1.5)
    v.clicar('#btn-agendar')
    v.pausa(1)
    v.passo('Horário disponível? Não: services.py recusa o conflito e a agenda é recarregada.')
    v.pausa(3.5)


def cena_registrar(v):
    v.clicar('#agenda-horarios .vs-slot')
    v.passo('Horário disponível? Sim: data + dia de atendimento + sem conflito.')
    v.digitar('#id_observacoes', 'Vacina V10 e pesagem')
    v.clicar('#btn-agendar')
    v.app.locator('#painel-sucesso').wait_for()
    v.passo('Consulta registrada (status "agendado"), ligada ao Animal e à Disponibilidade do dia.')
    v.pausa(3)


def cena_confirmar(v):
    v.clicar('#sucesso-whatsapp')
    v.passo('Confirmar: o status vira "confirmado" e o WhatsApp do tutor abre com a mensagem pronta.')
    v.pausa(2.5)
    v.clicar('#sucesso-detalhe')
    v.app.wait_for_load_state('networkidle')
    v.pausa(3)


def cena_atendimento(v):
    v.ir('/dashboard/')
    v.rolar(v.app.get_by_role('heading', name='Consultas de hoje'))
    v.passo('No dia: um clique registra o atendimento realizado ou a ausência do tutor.')
    v.pausa(1.5)
    v.clicar('[data-acao-status="realizado"]:visible')
    v.pausa(2)
    v.clicar('[data-acao-status="cancelado"]:visible')
    v.passo('Status atualizados pela API, sem recarregar a página.')
    v.pausa(2.5)


def cena_peso(v):
    v.ir('/animais/?q=Pa%C3%A7oca')
    v.clicar(v.app.get_by_role('link', name='Paçoca').first)
    v.esperar_url(r'/animais/\d+/$')
    v.ficha = v.app.url
    v.rolar('#titulo-peso')
    v.pausa(1.5)
    v.clicar(v.app.get_by_role('link', name=re.compile('Editar')).first)
    v.digitar('#id_peso', '8,9')
    v.clicar('#conteudo [type=submit]')
    v.esperar_url(r'/animais/$')  # a edição volta para a lista; abre a ficha de novo
    v.clicar('#conteudo a[href$="/animais/%d/"]' % int(re.search(r'/animais/(\d+)/', v.ficha).group(1)))
    v.esperar_url(r'/animais/\d+/$')
    v.rolar('#titulo-peso')
    v.passo('Cada novo peso grava uma pesagem: Animal 1:N Histórico de peso ("registra").')
    v.pausa(3.5)


def cena_transversal(v):
    v.ir('/consultas/agenda/')
    v.passo('Agenda semanal da clínica.')
    v.pausa(3)
    v.ir('/dashboard/')
    v.rolar('#analise-dados')
    v.passo('Análise de dados: totais, cancelamentos, ocupação e gráficos (API de estatísticas).')
    v.pausa(4)
    v.ir('/disponibilidade/')
    v.passo('Expediente da clínica: a entidade Disponibilidade.', der=['disponibilidade'])
    v.pausa(3)
    v.ir('/api/docs/')
    v.passo('API REST documentada (OpenAPI/Swagger). Também: acessibilidade, testes, nuvem e CI.', der=[])
    v.pausa(4)


def cena_fim(v):
    v.ir('/')
    v.pausa(3)


CENAS = [
    ('Página pública: horários livres', ['inicio', 'solicitar'], ['consulta', 'verifica', 'disponibilidade'], cena_publica),
    ('Login da veterinária', ['login', 'autenticar'], [], cena_login),
    ('Buscar proprietário e animal', ['buscar', 'sugerir'], ['proprietario', 'possui', 'animal'], cena_busca),
    ('Cadastrado? Não → cadastrar', ['cadastrado', 'cadastrar'], ['proprietario', 'possui', 'animal'], cena_cadastro),
    ('Consultar horários livres', ['horarios', 'agenda'], ['consulta', 'verifica', 'disponibilidade'], cena_agenda),
    ('Horário disponível? Não', ['selecionar', 'disponivel', 'agenda'], ['consulta', 'verifica', 'disponibilidade'], cena_conflito),
    ('Horário disponível? Sim → registrar', ['selecionar', 'disponivel', 'registrar'],
     ['animal', 'realiza', 'consulta', 'verifica', 'disponibilidade'], cena_registrar),
    ('Confirmar pelo WhatsApp', ['confirmar', 'receber'], ['consulta'], cena_confirmar),
    ('Atendimento e status', ['atendimento', 'status'], ['consulta'], cena_atendimento),
    ('Atualizar peso → histórico', ['peso', 'pesagem'], ['animal', 'registra', 'historico_peso'], cena_peso),
    ('Recursos transversais', ['transversal'], [], cena_transversal),
    ('Fim', ['fim'], [], cena_fim),
]


def converter(webm, marcas):
    """webm → mp4 completo + um mp4 por cena (cortado pelas marcas de tempo)."""
    if not shutil.which('ffmpeg'):
        print('ffmpeg não encontrado: ficou só o', webm)
        return
    codec = ['-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-an']
    completo = SAIDA / 'video_completo.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(webm), *codec, str(completo)], check=True)
    pasta = SAIDA / 'cenas'
    pasta.mkdir(exist_ok=True)
    for m in marcas:
        nome = pasta / f"cena_{m['numero']:02d}.mp4"
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f"{m['inicio']:.2f}", '-to', f"{m['fim']:.2f}",
                        '-i', str(completo), *codec, str(nome)], check=True)
    print('Vídeos em', SAIDA)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--ao-vivo', action='store_true', help='abre a janela e espera Enter antes de cada cena')
    p.add_argument('--sem-camera', action='store_true', help='não reserva o espaço da câmera no painel')
    p.add_argument('--ritmo', type=float, default=1.0, help='multiplica pausas e digitação (1.3 = mais lento)')
    p.add_argument('--cenas', help='só estas cenas, ex.: 3,4 (o login é feito antes, sem gravar à parte)')
    p.add_argument('--manter-banco', action='store_true', help='reaproveita o banco do vídeo anterior')
    a = p.parse_args()

    escolhidas = {int(n) for n in a.cenas.split(',')} if a.cenas else set(range(1, len(CENAS) + 1))
    ids = preparar_banco(a.manter_banco)
    servidor = subir_servidor()
    try:
        with sync_playwright() as pw:
            navegador = pw.chromium.launch(channel='chrome', headless=not a.ao_vivo,
                                           args=['--start-fullscreen'] if a.ao_vivo else [])
            opcoes = {'viewport': {'width': 1920, 'height': 1080}}
            if not a.ao_vivo:
                opcoes.update(record_video_dir=str(SAIDA / 'bruto'), record_video_size={'width': 1920, 'height': 1080})
            contexto = navegador.new_context(**opcoes)
            contexto.add_init_script(CURSOR_JS)
            palco = html_palco()
            contexto.route(BASE + '/__palco__*', lambda r: r.fulfill(body=palco, content_type='text/html; charset=utf-8'))

            page = contexto.new_page()
            contexto.on('page', lambda nova: nova.close())  # aba do WhatsApp: não abre no vídeo
            inicio = time.monotonic()
            page.goto(BASE + '/__palco__' + ('?sem-camera' if a.sem_camera else ''))
            v = Video(page, a.ritmo, ids)
            marcas = []
            for numero, (titulo, flx, der, funcao) in enumerate(CENAS, 1):
                if numero not in escolhidas:
                    if numero == 2:  # sem login as outras cenas não abrem
                        cena_login(v)
                    continue
                if a.ao_vivo:
                    input(f'[Enter] cena {numero}: {titulo} ')
                v.passo('', flx, der, cena=f'Cena {numero} de {len(CENAS)}', titulo=titulo)
                t0 = time.monotonic() - inicio
                funcao(v)
                marcas.append({'numero': numero, 'titulo': titulo, 'inicio': t0, 'fim': time.monotonic() - inicio})
                print(f'cena {numero:2d}  {t0:6.1f}s  {titulo}')
            if a.ao_vivo:
                input('[Enter] encerrar ')
            webm = page.video.path() if page.video else None
            contexto.close()
            navegador.close()
        if webm:
            (SAIDA / 'marcas.json').write_text(json.dumps(marcas, ensure_ascii=False, indent=1))
            converter(webm, marcas)
    finally:
        servidor.terminate()


if __name__ == '__main__':
    main()
