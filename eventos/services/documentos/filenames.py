import re
import unicodedata

from .types import DocumentoFormato, DocumentoOficioTipo, get_document_type_meta


def _normalize_filename_part(value):
    normalized = unicodedata.normalize('NFKD', str(value or ''))
    ascii_value = normalized.encode('ascii', 'ignore').decode('ascii')
    ascii_value = re.sub(r'[^a-zA-Z0-9]+', '_', ascii_value).strip('_').lower()
    return ascii_value or 'arquivo'


def _build_oficio_identifier(oficio):
    if oficio.numero and oficio.ano:
        return f'{int(oficio.numero):02d}_{int(oficio.ano)}'
    return f'rascunho_{oficio.pk or "sem_id"}'


def build_document_filename(oficio, tipo_documento, formato):
    meta = get_document_type_meta(tipo_documento)
    formato = DocumentoFormato(formato)
    identificador = _build_oficio_identifier(oficio)
    if meta.tipo == DocumentoOficioTipo.OFICIO:
        base_name = f'oficio_{identificador}'
    elif meta.tipo == DocumentoOficioTipo.JUSTIFICATIVA:
        base_name = f'justificativa_oficio_{identificador}'
    elif meta.tipo == DocumentoOficioTipo.TERMO_AUTORIZACAO:
        base_name = f'termo_autorizacao_oficio_{identificador}'
    elif meta.tipo == DocumentoOficioTipo.PLANO_TRABALHO:
        base_name = f'plano_trabalho_oficio_{identificador}'
    elif meta.tipo == DocumentoOficioTipo.ORDEM_SERVICO:
        base_name = f'ordem_servico_oficio_{identificador}'
    else:
        base_name = f'{meta.slug}_oficio_{identificador}'
    return f'{_normalize_filename_part(base_name)}.{formato.value}'
