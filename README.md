# VETSystem — Sistema de Agendamento Veterinário

> Projeto Integrador em Computação I (PJI110) — UNIVESP 2026

Sistema de agendamento desenvolvido para a clínica **ATIVO PET — Fisioterapia e Bem-Estar Animal** (Limeira/SP), substituindo o controle manual via WhatsApp por uma solução web centralizada.

## Stack

- **Backend:** Python 3.12 + Django 5.x
- **Frontend:** Tailwind CSS (CDN)
- **Banco (dev):** SQLite | **Banco (prod):** PostgreSQL
- **Deploy:** Railway

## Instalação local

```bash
# 1. Clone o repositório
git clone https://github.com/lerocha1194/vetsystem.git
cd vetsystem

# 2. Crie o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env

# 5. Execute as migrações
python manage.py migrate

# 6. Crie um superusuário
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

Acesse em: http://127.0.0.1:8000

## Grupo

| Nome | RA |
|---|---|
| Alison Ferreira Cabral | 2213917 |
| Denize Aparecida Graciano | 24203934 |
| Eder de Paula Evangelista | 23201277 |
| Lucas Eduardo Rocha | 24217901 |
| Miúcha Carvalho Cicaroni | 23212531 |
| Reginaldo Aparecido Matioli | 1501071 |
| Samuel de Souza Rodrigues | 23219876 |
| Yuri Liston | 24203775 |

## Orientador

Prof. Eduardo Maurício Moreno Pinto — UNIVESP

---

*Desenvolvido para a disciplina PJI110 — Projeto Integrador em Computação I, 2026.*
