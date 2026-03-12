# -*- coding: utf-8 -*-
"""Utilitários do app eventos."""

import re

from django.db.models import Q

from cadastros.models import Veiculo
from core.utils.masks import (
    format_placa,
    format_protocolo,
    normalize_placa,
    normalize_protocolo,
    only_digits,
)


def hhmm_to_minutes(value):
    """
    Converte string HH:MM em minutos.
    Ex.: "03:30" -> 210, "01:05" -> 65, "00:45" -> 45.
    Aceita HH de 0 a 99, MM de 0 a 59.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    s = str(value).strip()
    match = re.match(r'^(\d{1,2}):([0-5]?\d)$', s)
    if not match:
        raise ValueError('Use o formato HH:MM (ex.: 03:30).')
    horas, minutos = int(match.group(1)), int(match.group(2))
    if horas < 0 or minutos < 0 or minutos > 59:
        raise ValueError('Minutos devem ser 00 a 59.')
    return horas * 60 + minutos


def minutes_to_hhmm(minutes):
    """
    Converte minutos em string HH:MM.
    Ex.: 210 -> "03:30", 65 -> "01:05".
    """
    if minutes is None:
        return ''
    try:
        total = int(minutes)
    except (TypeError, ValueError):
        return ''
    if total < 0:
        return ''
    horas, minutos = divmod(total, 60)
    return f'{horas:02d}:{minutos:02d}'


def mapear_tipo_viatura_para_oficio(tipo_veiculo):
    """Converte o tipo do cadastro de veículo para o tipo persistido no ofício."""
    tipo = (tipo_veiculo or '').strip().upper()
    if tipo == Veiculo.TIPO_CARACTERIZADO:
        return 'CARACTERIZADA'
    return 'DESCARACTERIZADA'


def buscar_veiculo_finalizado_por_placa(placa):
    """Busca veículo finalizado pela placa canônica."""
    placa_normalizada = normalize_placa(placa)
    if not placa_normalizada:
        return None
    return (
        Veiculo.objects.select_related('combustivel')
        .filter(status=Veiculo.STATUS_FINALIZADO, placa=placa_normalizada)
        .first()
    )


def buscar_veiculos_finalizados(termo, limit=10):
    """Busca viaturas finalizadas por placa ou modelo para o Step 2 do ofício."""
    termo_limpo = str(termo or '').strip()
    if not termo_limpo:
        return []

    termo_placa = normalize_placa(termo_limpo)
    queryset = Veiculo.objects.select_related('combustivel').filter(status=Veiculo.STATUS_FINALIZADO)
    filtros = Q(modelo__icontains=termo_limpo)
    if termo_placa:
        filtros |= Q(placa__icontains=termo_placa)
    return list(queryset.filter(filtros).order_by('placa', 'modelo')[:limit])


def serializar_veiculo_para_oficio(veiculo):
    """Serializa os dados do veículo no formato usado pelo Step 2 do ofício."""
    if not veiculo:
        return {
            'placa': '',
            'placa_formatada': '',
            'modelo': '',
            'combustivel': '',
            'tipo_viatura': 'DESCARACTERIZADA',
            'tipo_viatura_label': 'Descaracterizada',
        }

    tipo_viatura = mapear_tipo_viatura_para_oficio(veiculo.tipo)
    tipo_viatura_label = 'Caracterizada' if tipo_viatura == 'CARACTERIZADA' else 'Descaracterizada'
    return {
        'placa': veiculo.placa,
        'placa_formatada': format_placa(veiculo.placa),
        'modelo': veiculo.modelo or '',
        'combustivel': veiculo.combustivel.nome if veiculo.combustivel_id else '',
        'tipo_viatura': tipo_viatura,
        'tipo_viatura_label': tipo_viatura_label,
    }
