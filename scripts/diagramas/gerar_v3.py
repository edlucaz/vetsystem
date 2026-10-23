"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : scripts/diagramas/gerar_v3.py
Função  : Gera o DER v3 e o fluxograma v3 (versão final do PI II) em SVG, no mesmo
          estilo das Figuras 1 e 2 do relatório parcial, com as mudanças do
          Apêndice A do docs/PLANO_PI2.md. Cada entidade, relacionamento e etapa
          ganha um id (der-*, flx-*), usado para destacar no vídeo (scripts/video).
          Uso: .venv/bin/python scripts/diagramas/gerar_v3.py  (grava em docs/diagramas/)
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-23
"""
from pathlib import Path

SAIDA = Path(__file__).resolve().parents[2] / 'docs' / 'diagramas'
FONTE = "font-family=\"'Noto Sans','DejaVu Sans',Arial,sans-serif\""

# Estilos da legenda: herdado do PI1, incluído no DER no PI2 (azul) e novo no PI2 (verde)
AZUL = 'stroke="#2563EB" stroke-width="2.2" stroke-dasharray="3 3"'
VERDE = 'stroke="#16A34A" stroke-width="2.2" stroke-dasharray="7 4"'
LARANJA = 'stroke="#D97706" stroke-width="2.2" stroke-dasharray="2 3"'
PRETO = 'stroke="#000000" stroke-width="1.5"'


def texto(x, y, conteudo, tam=12, peso='normal', cor='#000000', ancora='middle', extra=''):
    return (f'<text x="{x}" y="{y}" text-anchor="{ancora}" dominant-baseline="central" {FONTE} '
            f'font-size="{tam}" font-weight="{peso}" fill="{cor}"{extra}>{conteudo}</text>')


# =============================================================================
# DER v3
# =============================================================================

def der():
    linhas, formas = [], []

    def entidade(chave, x, y, larg, nome, estilo=PRETO, atributos=()):
        """Entidade + atributos num <g id="der-chave">. atributos: (nome, x, y, tipo, estilo)."""
        g = [f'<g id="der-{chave}" class="der-item">']
        for nome_at, ax, ay, tipo, est in atributos:
            cor = '#16A34A' if est == VERDE else '#2563EB' if est == AZUL else '#000000'
            traco = ' stroke-dasharray="3 3"' if est else ''
            g.append(f'<line x1="{x}" y1="{y}" x2="{ax}" y2="{ay}" stroke="{cor}" stroke-width="1.5"{traco}/>')
        g.append(f'<rect x="{x - larg / 2}" y="{y - 20}" width="{larg}" height="40" fill="#DBEAFE" {estilo}/>')
        g.append(texto(x, y, nome, 14, 'bold'))
        for nome_at, ax, ay, tipo, est in atributos:
            rx = max(22.8, len(nome_at) * 3.6 + 8)
            g.append(f'<ellipse cx="{ax}" cy="{ay}" rx="{rx:.1f}" ry="14" fill="#FFFFFF" {est or PRETO}/>')
            g.append(texto(ax, ay, nome_at, extra=' text-decoration="underline"' if tipo == 'pk' else ''))
        g.append('</g>')
        formas.append('\n'.join(g))

    def relacionamento(chave, x, y, nome, segmentos, card, estilo=PRETO, cor_linha='#000000', nota=()):
        g = [f'<g id="der-{chave}" class="der-item">']
        for x1, y1, x2, y2 in segmentos:
            g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cor_linha}" stroke-width="2"/>')
        g.append(f'<polygon points="{x - 40},{y} {x},{y - 30} {x + 40},{y} {x},{y + 30}" fill="#FEF9C3" {estilo}/>')
        g.append(texto(x, y, nome, 13))
        for cx, cy, c in card:
            g.append(texto(cx, cy, c, 13, 'bold'))
        for nx, ny, n in nota:
            g.append(texto(nx, ny, n, 10.5, cor='#15803D', ancora='end'))
        g.append('</g>')
        formas.append('\n'.join(g))

    entidade('proprietario', 165, 280, 150, 'PROPRIETÁRIO', atributos=(
        ('id_proprietario', 110, 137, 'pk', None), ('nome', 62, 208, '', None), ('cpf', 50, 280, '', None),
        ('telefone', 65, 353, '', None), ('email', 112, 417, '', None)))
    entidade('animal', 470, 280, 110, 'ANIMAL', atributos=(
        ('id_animal', 470, 115, 'pk', None), ('nome', 385, 135, '', None), ('especie', 545, 125, '', None),
        ('raca', 365, 195, '', None), ('data_nascimento', 610, 215, '', None),
        ('id_proprietario (FK)', 340, 385, '', None),
        ('peso', 560, 340, '', VERDE), ('queixa', 585, 395, '', VERDE)))
    entidade('consulta', 775, 280, 120, 'CONSULTA', atributos=(
        ('id_consulta', 775, 133, 'pk', None), ('data_hora', 890, 170, '', None),
        ('tipo_atendimento', 912, 243, '', None), ('status', 912, 318, '', None),
        ('observacoes', 900, 385, '', None), ('id_animal (FK)', 690, 375, '', None),
        ('duracao_minutos', 665, 150, '', VERDE), ('id_disponibilidade (FK)', 870, 505, '', VERDE)))
    entidade('disponibilidade', 775, 600, 170, 'DISPONIBILIDADE', estilo=AZUL, atributos=(
        ('id_disponibilidade', 640, 670, 'pk', AZUL), ('dia_semana', 925, 560, '', AZUL),
        ('hora_inicio', 705, 730, '', AZUL), ('hora_fim', 860, 730, '', AZUL), ('ativo', 930, 650, '', VERDE)))
    entidade('historico_peso', 470, 640, 170, 'HISTÓRICO_PESO', estilo=VERDE, atributos=(
        ('id_registro', 290, 610, 'pk', VERDE), ('data', 300, 680, '', VERDE),
        ('peso', 560, 730, '', VERDE), ('id_animal (FK)', 400, 740, '', VERDE)))

    relacionamento('possui', 335, 280, 'possui', [(240, 280, 295, 280), (375, 280, 415, 280)],
                   [(270, 266, '1'), (395, 266, 'N')])
    relacionamento('realiza', 640, 280, 'realiza', [(525, 280, 600, 280), (680, 280, 715, 280)],
                   [(565, 266, '1'), (698, 266, 'N')])
    relacionamento('verifica', 775, 450, 'verifica', [(775, 300, 775, 420), (775, 480, 775, 580)],
                   [(790, 330, 'N'), (790, 560, '1')], estilo=VERDE, cor_linha='#16A34A',
                   nota=((728, 444, 'FK Consulta.disponibilidade'), (728, 458, '+ endpoint de horários livres')))
    relacionamento('registra', 470, 510, 'registra', [(470, 300, 470, 480), (470, 540, 470, 620)],
                   [(484, 320, '1'), (484, 595, 'N')], estilo=VERDE, cor_linha='#16A34A')

    legenda = f'''<g id="der-legenda">
<rect x="30" y="790" width="940" height="140" rx="8" fill="#F9F9F7" stroke="#888780" stroke-width="0.8"/>
{texto(500, 808, 'Legenda', 13, 'bold')}
<line x1="50" y1="822" x2="950" y2="822" stroke="#D3D1C7" stroke-width="0.8"/>
<rect x="50" y="835" width="32" height="20" fill="#DBEAFE" {PRETO}/>{texto(90, 845, 'Entidade', ancora='start')}
<ellipse cx="190" cy="845" rx="22" ry="10" fill="#fff" {PRETO}/>{texto(220, 845, 'Atributo', ancora='start')}
<ellipse cx="310" cy="845" rx="22" ry="10" fill="#fff" {PRETO}/>{texto(310, 845, 'PK', 10, extra=' text-decoration="underline"')}
{texto(340, 845, 'Chave primária (sublinhado)', ancora='start')}
{texto(530, 845, '(FK)', peso='bold', ancora='start')}{texto(565, 845, 'Chave estrangeira', ancora='start')}
<polygon points="720,835 740,845 720,855 700,845" fill="#FEF9C3" {PRETO}/>{texto(750, 845, 'Relacionamento', ancora='start')}
<rect x="50" y="869" width="32" height="20" fill="#DBEAFE" {PRETO}/>{texto(90, 879, 'Herdado do PI1', ancora='start')}
<rect x="230" y="869" width="32" height="20" fill="#DBEAFE" {AZUL}/>{texto(270, 879, 'Incluído no DER no PI2 (já existia no código do PI1)', ancora='start')}
<rect x="640" y="869" width="32" height="20" fill="#FEF9C3" {VERDE}/>{texto(680, 879, 'Novo no PI2', ancora='start')}
{texto(680, 900, 'FK verifica, histórico de peso e novos atributos', 11, cor='#444444', ancora='start')}
</g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="970" viewBox="0 0 1000 970">
<rect width="1000" height="970" fill="#FFFFFF"/>
{texto(500, 26, 'Figura 2 – Diagrama de Entidade-Relacionamento do VETSystem (versão final, PI II)', 14, 'bold')}
{chr(10).join(linhas + formas)}
{legenda}
{texto(500, 950, 'Fonte: elaborado pelos autores (2026).', 11, cor='#444444')}
</svg>
'''


# =============================================================================
# Fluxograma v3 (swimlane: Tutor · Veterinária · VETSystem)
# =============================================================================

ATOR = {  # preenchimento, borda, cor do título, cor do subtítulo
    'tutor': ('#9FE1CB', '#0F6E56', '#04342C', '#0F6E56'),
    'vet': ('#CECBF6', '#534AB7', '#26215C', '#534AB7'),
    'sis': ('#E8E7E3', '#B4B2A9', '#2C2C2A', '#5F5E5A'),
    'reg': ('#B5D4F4', '#185FA5', '#042C53', '#185FA5'),
}
COLUNA = {'tutor': 160, 'vet': 450, 'sis': 740}
COR_MARCA = {'evo': '#D97706', 'novo': '#16A34A'}


def fluxograma():
    setas, nos = [], []

    def no(chave, ator, coluna, y, titulo, subs=(), versao='', marca=None, cor='tutor'):
        """Processo (retângulo) com id flx-chave. versao: '', 'evo' (laranja) ou 'novo' (verde)."""
        x = COLUNA[coluna]
        fundo, borda, c_tit, c_sub = ATOR[ator]
        alt = 54 + 15 * max(0, len(subs) - 1)
        estilo = {'evo': LARANJA, 'novo': VERDE}.get(versao, f'stroke="{borda}" stroke-width="0.8"')
        g = [f'<g id="flx-{chave}" class="flx-item">',
             f'<rect x="{x - 118}" y="{y}" width="236" height="{alt}" rx="7" fill="{fundo}" {estilo}/>',
             texto(x, y + 18, titulo, 14, '500', c_tit)]
        for i, s in enumerate(subs):
            g.append(texto(x, y + 38 + 15 * i, s, 11.5, cor=c_sub))
        if marca:
            g.append(f'<circle cx="{x + 114}" cy="{y + 2}" r="10" fill="{COR_MARCA[versao]}" stroke="#FFFFFF" stroke-width="1.5"/>')
            g.append(texto(x + 114, y + 2, marca, 11, 'bold', '#FFFFFF'))
        g.append('</g>')
        nos.append('\n'.join(g))

    def decisao(chave, y, titulo, subs, versao='', marca=None):
        x = COLUNA['sis']
        estilo = LARANJA if versao == 'evo' else 'stroke="#854F0B" stroke-width="0.8"'
        g = [f'<g id="flx-{chave}" class="flx-item">',
             f'<polygon points="{x},{y} {x + 118},{y + 54} {x},{y + 108} {x - 118},{y + 54}" fill="#FAEEDA" {estilo}/>',
             texto(x, y + 44, titulo, 13.5, '500', '#412402')]
        for i, s in enumerate(subs):
            g.append(texto(x, y + 63 + 14 * i, s, 10.5, cor='#854F0B'))
        if marca:
            g.append(f'<circle cx="{x + 67}" cy="{y + 21}" r="10" fill="{COR_MARCA[versao]}" stroke="#FFFFFF" stroke-width="1.5"/>')
            g.append(texto(x + 67, y + 21, marca, 11, 'bold', '#FFFFFF'))
        g.append('</g>')
        nos.append('\n'.join(g))

    def terminal(chave, coluna, y, rotulo):
        x = COLUNA[coluna]
        nos.append(f'<g id="flx-{chave}" class="flx-item"><rect x="{x - 75}" y="{y}" width="150" height="40" rx="20" '
                   f'fill="#D3D1C7" stroke="#888780" stroke-width="0.8"/>{texto(x, y + 20, rotulo, 14, "500", "#2C2C2A")}</g>')

    def seta(d, rotulo=None, pos=None, ancora='start', tracejada=False):
        traco = ' stroke-dasharray="5 4"' if tracejada else ''
        setas.append(f'<path d="{d}" fill="none" stroke="#6B6A64" stroke-width="1.2"{traco} marker-end="url(#seta)"/>')
        if rotulo:
            setas.append(texto(pos[0], pos[1], rotulo, 12, '500', '#444441', ancora))

    terminal('inicio', 'tutor', 110, 'Início')
    no('solicitar', 'tutor', 'tutor', 188, 'Solicitar agendamento',
       ('telefone, WhatsApp ou presencial', '(vê horários livres no site)'), 'evo', '6')
    no('login', 'vet', 'vet', 188, 'Realizar login', ('usuário e senha',))
    no('autenticar', 'sis', 'sis', 188, 'Autenticar usuário', ('sessão Django + API autenticada',), 'evo', '1')
    no('buscar', 'vet', 'vet', 288, 'Buscar proprietário', ('digita nome do tutor ou do animal',))
    no('sugerir', 'sis', 'sis', 368, 'Sugerir proprietário e animal',
       ('busca rápida ou lista com filtros', '(API REST + JavaScript)'), 'evo', '2')
    decisao('cadastrado', 460, 'Cadastrado?', ('proprietário + animal',))
    no('cadastrar', 'vet', 'vet', 487, 'Cadastrar proprietário', ('e animal', '(volta direto ao agendamento)'))
    no('horarios', 'sis', 'sis', 600, 'Consultar horários livres', ('Consulta × Disponibilidade (API)',), 'novo', '3')
    no('agenda', 'sis', 'sis', 690, 'Exibir agenda interativa', ('calendário em JS (assíncrono)',), 'evo', '4')
    no('selecionar', 'vet', 'vet', 690, 'Selecionar horário', ('data, tipo, observações',))
    decisao('disponivel', 770, 'Horário disponível?', ('data + Disponibilidade', '+ sem conflito'), 'evo', '5')
    no('registrar', 'reg', 'sis', 910, 'Registrar consulta', ('status: agendado',))
    no('confirmar', 'vet', 'vet', 910, 'Confirmar agendamento',
       ('status: confirmado', 'aviso pelo WhatsApp'), 'evo', '7')
    no('receber', 'tutor', 'tutor', 910, 'Receber confirmação', ('WhatsApp / telefone',))
    no('atendimento', 'vet', 'vet', 1015, 'Realizar atendimento', ('ou registrar ausência',))
    no('status', 'reg', 'sis', 1015, 'Atualizar status', ('realizado / cancelado (ausência)',))
    no('peso', 'vet', 'vet', 1110, 'Atualizar peso do animal', ('(opcional, na ficha do animal)',), 'novo', '8')
    no('pesagem', 'reg', 'sis', 1110, 'Registrar pesagem', ('histórico de peso do animal',))
    terminal('fim', 'sis', 1205, 'Fim')

    seta('M160,150 L160,186')
    seta('M278,215 L330,215')
    seta('M568,215 L620,215')
    seta('M740,242 L740,315 L570,315')
    seta('M450,342 L450,405 L620,405')
    seta('M740,437 L740,458')
    seta('M622,514 L570,514', 'Não', (596, 502), 'middle')
    seta('M450,556 L450,627 L620,627')
    seta('M740,568 L740,598', 'Sim', (756, 584))
    seta('M740,654 L740,688')
    seta('M622,717 L570,717')
    seta('M450,744 L450,824 L620,824')
    seta('M858,824 L870,824 L870,717 L860,717', 'Não', (866, 780), 'end')
    seta('M740,878 L740,908', 'Sim', (756, 893))
    seta('M622,940 L570,940')
    seta('M332,940 L280,940')
    seta('M160,984 L160,1042 L330,1042', 'no dia agendado', (172, 1030))
    seta('M568,1042 L620,1042')
    seta('M450,1069 L450,1108', 'opcional', (462, 1090), tracejada=True)
    seta('M568,1137 L620,1137')
    seta('M740,1069 L740,1100 L862,1100 L862,1225 L817,1225')
    seta('M740,1164 L740,1203')

    altura = 1660
    itens = [
        ('1', 'evo', 'Autenticação: além do login por sessão,', 'a API REST usa a mesma sessão + CSRF'),
        ('2', 'evo', 'Busca: autocomplete pela API ou janela', 'com abas Tutor/Animal e filtros'),
        ('3', 'novo', 'Endpoint de horários livres: cruza consultas', 'agendadas com a Disponibilidade da clínica'),
        ('4', 'evo', 'Tela de horários vira agenda interativa', 'em JavaScript (sem recarregar a página)'),
        ('5', 'evo', 'Validação: data + dia de atendimento +', 'expediente + conflito (services.py)'),
        ('6', 'evo', 'Tutor vê os próximos horários livres', 'na página inicial e chama no WhatsApp'),
        ('7', 'evo', 'Confirmação muda o status para', '"confirmado" e abre o WhatsApp do tutor'),
        ('8', 'novo', 'Histórico de peso: cada atualização', 'grava uma pesagem (RegistroPeso)'),
    ]
    leg = [f'<rect x="20" y="1270" width="860" height="350" rx="8" fill="#F9F9F7" stroke="#888780" stroke-width="0.8"/>',
           texto(450, 1290, 'Legenda', 14, 'bold', '#2C2C2A'),
           '<line x1="40" y1="1306" x2="860" y2="1306" stroke="#D3D1C7" stroke-width="0.8"/>',
           texto(40, 1326, 'Formas', 12, cor='#5F5E5A', ancora='start'),
           '<rect x="40" y="1340" width="34" height="20" rx="4" fill="#E8E7E3" stroke="#B4B2A9" stroke-width="0.8"/>',
           texto(82, 1350, 'Processo', ancora='start'),
           '<polygon points="177,1340 194,1350 177,1360 160,1350" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.8"/>',
           texto(202, 1350, 'Decisão', ancora='start'),
           '<rect x="270" y="1340" width="34" height="20" rx="10" fill="#D3D1C7" stroke="#888780" stroke-width="0.8"/>',
           texto(312, 1350, 'Início / Fim', ancora='start'),
           texto(40, 1382, 'Atores', 12, cor='#5F5E5A', ancora='start')]
    for i, (rot, ator) in enumerate((('Tutor', 'tutor'), ('Veterinária', 'vet'), ('Sistema', 'sis'), ('Registro', 'reg'))):
        f, b, _, _ = ATOR[ator]
        x = 40 + i * 95
        leg.append(f'<rect x="{x}" y="1396" width="22" height="18" rx="4" fill="{f}" stroke="{b}" stroke-width="0.8"/>')
        leg.append(texto(x + 30, 1405, rot, ancora='start'))
    leg += [texto(40, 1437, 'Versão', 12, cor='#5F5E5A', ancora='start'),
            '<rect x="40" y="1451" width="34" height="20" rx="4" fill="#E8E7E3" stroke="#B4B2A9" stroke-width="0.8"/>',
            texto(82, 1461, 'Herdado do PI1 (sem alteração)', ancora='start'),
            f'<rect x="40" y="1479" width="34" height="20" rx="4" fill="#E8E7E3" {LARANJA}/>',
            texto(82, 1489, 'Evoluído no PI2 (existia no PI1)', ancora='start'),
            f'<rect x="40" y="1507" width="34" height="20" rx="4" fill="#E8E7E3" {VERDE}/>',
            texto(82, 1517, 'Novo no PI2 (não existia no PI1)', ancora='start'),
            '<line x1="440" y1="1318" x2="440" y2="1605" stroke="#D3D1C7" stroke-width="0.8"/>',
            texto(458, 1326, 'O que mudou do PI1 para o PI2', 12, cor='#5F5E5A', ancora='start')]
    for i, (num, versao, l1, l2) in enumerate(itens):
        y = 1352 + i * 31
        leg.append(f'<circle cx="468" cy="{y}" r="9" fill="{COR_MARCA[versao]}" stroke="#FFFFFF" stroke-width="1.5"/>')
        leg.append(texto(468, y, num, 10.5, 'bold', '#FFFFFF'))
        leg.append(texto(484, y - 7, l1, 11, cor='#2C2C2A', ancora='start'))
        leg.append(texto(484, y + 7, l2, 11, cor='#2C2C2A', ancora='start'))
    leg.append(f'<g id="flx-transversal" class="flx-item">'
               f'<rect x="36" y="1537" width="396" height="74" rx="6" fill="#F0FDF4" {VERDE}/>'
               + texto(48, 1551, 'Transversal a todas as etapas (PI2):', 11.5, 'bold', '#15803D', 'start')
               + texto(48, 1568, 'acessibilidade WCAG 2.1 AA · testes automatizados', 11, cor='#2C2C2A', ancora='start')
               + texto(48, 1583, 'análise de dados · agenda semanal · API documentada', 11, cor='#2C2C2A', ancora='start')
               + texto(48, 1598, 'nuvem: Render + Neon · deploy automático · branches + PR', 11, cor='#2C2C2A', ancora='start')
               + '</g>')

    raias = []
    for x, nome, fundo in ((20, 'Tutor', '#F5F5F2'), (310, 'Veterinária (Sra. Fernanda)', '#F5F5F2'),
                           (600, 'VETSystem (Django + API REST)', '#EDECE8')):
        raias.append(f'<rect x="{x}" y="50" width="280" height="1205" rx="6" fill="{fundo}" stroke="#C8C7BE" stroke-width="0.8"/>')
        raias.append(texto(x + 140, 70, nome, 13, '500', '#444441'))
        raias.append(f'<line x1="{x}" y1="90" x2="{x + 280}" y2="90" stroke="#C8C7BE" stroke-width="0.8"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{altura}" viewBox="0 0 900 {altura}">
<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#6B6A64" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
<rect width="900" height="{altura}" fill="#FFFFFF"/>
{texto(450, 24, 'Figura 1 – Fluxograma de agendamento do VETSystem / Ativo Pet (versão final, PI II)', 14, 'bold')}
{chr(10).join(raias)}
{chr(10).join(setas)}
{chr(10).join(nos)}
{chr(10).join(leg)}
{texto(450, 1640, 'Fonte: elaborado pelos autores (2026).', 11.5, cor='#444444')}
</svg>
'''


if __name__ == '__main__':
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / 'der_v3.svg').write_text(der(), encoding='utf-8')
    (SAIDA / 'fluxograma_v3.svg').write_text(fluxograma(), encoding='utf-8')
    print(f'Gerados: {SAIDA / "der_v3.svg"} e {SAIDA / "fluxograma_v3.svg"}')
