"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : scripts/video/settings_video.py
Função  : Configurações só para gravar o vídeo: as mesmas do projeto, mas permitindo que o
          sistema abra dentro do iframe do palco (mesma origem). Não usar em produção.
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-23
"""
from vetsystem.settings import *  # noqa: F401,F403

X_FRAME_OPTIONS = 'SAMEORIGIN'
