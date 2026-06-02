import re
import unicodedata

from core.utils.masks import EMPTY_MASK_DISPLAY

from .types import DocumentoFormato, DocumentoOficioTipo, get_document_type_meta


def _normalize_filename_part(value):
    normalized = unicodedata.normalize('NFKD', str(value or ''))
    ascii_value = normalized.encode('ascii', 'ignore').decode('ascii')
    ascii_value = re.sub(r'[^a-zA-Z0-9]+', '_', ascii_value).strip('_').lower()
    return ascii_value or 'arquivo'


def _has_filename_content(value):
    return bool(re.search(r'[A-Za-z0-9]', str(value or '')))


def _build_document_number_label(value, fallback):
    text = str(value or '').strip()
    if text and text != EMPTY_MASK_DISPLAY and _has_filename_content(text):
        return text
    return fallback


def _build_first_name(value):
    text = str(value or '').strip()
    if not text:
        return ''
    return text.split()[0]


def _collect_unique_labels(values, fallback):
    labels = []
    seen = set()
    for value in values or []:
        label = _normalize_filename_part(value)
        if label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return '_'.join(labels) if labels else fallback


def _build_oficio_destino_label(oficio):
    labels = []
    seen = set()
    roteiro = getattr(oficio, 'roteiro_evento', None)
    if roteiro:
        queryset = roteiro.destinos.select_related('cidade', 'estado').order_by('ordem', 'pk')
        for destino in queryset:
            if destino.cidade_id and destino.estado_id:
                label = f'{destino.cidade.nome}/{destino.estado.sigla}'
            elif destino.cidade_id:
                label = destino.cidade.nome
            elif destino.estado_id:
                label = destino.estado.sigla
            else:
                label = ''
            label = str(label or '').strip()
            if label and label not in seen:
                seen.add(label)
                labels.append(label)
    if not labels:
        queryset = oficio.trechos.select_related('destino_cidade', 'destino_estado').order_by('ordem', 'pk')
        for trecho in queryset:
            if trecho.destino_cidade_id and trecho.destino_estado_id:
                label = f'{trecho.destino_cidade.nome}/{trecho.destino_estado.sigla}'
            elif trecho.destino_cidade_id:
                label = trecho.destino_cidade.nome
            elif trecho.destino_estado_id:
                label = trecho.destino_estado.sigla
            else:
                label = ''
            label = str(label or '').strip()
            if label and label not in seen:
                seen.add(label)
                labels.append(label)
    if not labels:
        evento = oficio.eventos.select_related().first() if hasattr(oficio, 'eventos') else None
        if evento:
            queryset = evento.destinos.select_related('cidade', 'estado').order_by('ordem', 'pk')
            for destino in queryset:
                if destino.cidade_id and destino.estado_id:
                    label = f'{destino.cidade.nome}/{destino.estado.sigla}'
                elif destino.cidade_id:
                    label = destino.cidade.nome
                elif destino.estado_id:
                    label = destino.estado.sigla
                else:
                    label = ''
                label = str(label or '').strip()
                if label and label not in seen:
                    seen.add(label)
                    labels.append(label)
    return _collect_unique_labels(labels, 'destino')


def _build_oficio_servidores_label(oficio):
    labels = []
    seen = set()
    queryset = oficio.viajantes.select_related('cargo').order_by('nome')
    for viajante in queryset:
        first_name = _build_first_name(getattr(viajante, 'nome', ''))
        if not first_name:
            continue
        normalized = _normalize_filename_part(first_name)
        if normalized in seen:
            continue
        seen.add(normalized)
        labels.append(first_name)
    return _collect_unique_labels(labels, 'servidor')


def _build_oficio_number_label(oficio):
    return _build_document_number_label(getattr(oficio, 'numero_formatado', ''), 'rascunho')


def _build_plano_number_label(plano):
    return _build_document_number_label(getattr(plano, 'numero_formatado', ''), 'rascunho')


def _build_plano_destino_label(plano):
    destinos = []
    if hasattr(plano, 'get_destinos_labels'):
        destinos = [label for label in plano.get_destinos_labels() if label]
    return _collect_unique_labels(destinos, 'destino')


def build_termo_autorizacao_filename(servidor, destino, formato, prefix='termo_autorizacao'):
    formato = DocumentoFormato(formato)
    servidor_label = _normalize_filename_part(servidor) if servidor else 'servidor'
    destino_label = _normalize_filename_part(destino) if destino else 'destino'
    base_name = f'{prefix}_{servidor_label}_{destino_label}'
    return f'{_normalize_filename_part(base_name)}.{formato.value}'


def build_document_filename(oficio, tipo_documento, formato):
    meta = get_document_type_meta(tipo_documento)
    formato = DocumentoFormato(formato)
    if meta.tipo == DocumentoOficioTipo.OFICIO:
        base_name = f'oficio_{_build_oficio_number_label(oficio)}_{_build_oficio_destino_label(oficio)}_{_build_oficio_servidores_label(oficio)}'
    elif meta.tipo == DocumentoOficioTipo.JUSTIFICATIVA:
        base_name = f'justificativa_oficio_{_build_oficio_number_label(oficio)}_{_build_oficio_destino_label(oficio)}_{_build_oficio_servidores_label(oficio)}'
    elif meta.tipo == DocumentoOficioTipo.TERMO_AUTORIZACAO:
        base_name = build_termo_autorizacao_filename(
            _build_oficio_servidores_label(oficio),
            _build_oficio_destino_label(oficio),
            formato,
        ).rsplit('.', 1)[0]
    elif meta.tipo == DocumentoOficioTipo.PLANO_TRABALHO:
        base_name = f'plano_trabalho_{_build_plano_number_label(oficio)}_{_build_plano_destino_label(oficio)}'
    elif meta.tipo == DocumentoOficioTipo.ORDEM_SERVICO:
        base_name = f'ordem_servico_oficio_{_build_oficio_number_label(oficio)}_{_build_oficio_destino_label(oficio)}'
    else:
        base_name = f'{meta.slug}_oficio_{_build_oficio_number_label(oficio)}_{_build_oficio_destino_label(oficio)}'
    return f'{_normalize_filename_part(base_name)}.{formato.value}'
