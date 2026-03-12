from dataclasses import dataclass
from enum import Enum


class DocumentoFormato(str, Enum):
    DOCX = 'docx'
    PDF = 'pdf'


class DocumentoOficioTipo(str, Enum):
    OFICIO = 'OFICIO'
    JUSTIFICATIVA = 'JUSTIFICATIVA'
    PLANO_TRABALHO = 'PLANO_TRABALHO'
    ORDEM_SERVICO = 'ORDEM_SERVICO'
    TERMO_AUTORIZACAO = 'TERMO_AUTORIZACAO'


@dataclass(frozen=True)
class DocumentoTipoMeta:
    tipo: DocumentoOficioTipo
    slug: str
    label: str
    implemented_formats: tuple[DocumentoFormato, ...] = ()

    @property
    def implemented(self):
        return bool(self.implemented_formats)

    def supports(self, formato):
        try:
            normalized = DocumentoFormato(formato)
        except ValueError:
            return False
        return normalized in self.implemented_formats


class DocumentGenerationError(Exception):
    """Erro base da camada documental."""


class DocumentValidationError(DocumentGenerationError):
    """Documento não pode ser gerado por pendência de negócio."""


class DocumentFormatNotAvailable(DocumentGenerationError):
    """Formato ainda não suportado nesta fase."""


class DocumentRendererUnavailable(DocumentGenerationError):
    """Backend de renderização indisponível no ambiente atual."""


class DocumentTemplateUnavailable(DocumentGenerationError):
    """Modelo DOCX indisponível para o tipo documental."""


class DocumentTypeNotImplemented(DocumentGenerationError):
    """Tipo documental ainda não implementado nesta fase."""


_DOCUMENT_TYPE_REGISTRY = {
    DocumentoOficioTipo.OFICIO: DocumentoTipoMeta(
        tipo=DocumentoOficioTipo.OFICIO,
        slug='oficio',
        label='Ofício',
        implemented_formats=(DocumentoFormato.DOCX, DocumentoFormato.PDF),
    ),
    DocumentoOficioTipo.JUSTIFICATIVA: DocumentoTipoMeta(
        tipo=DocumentoOficioTipo.JUSTIFICATIVA,
        slug='justificativa',
        label='Justificativa',
        implemented_formats=(DocumentoFormato.DOCX, DocumentoFormato.PDF),
    ),
    DocumentoOficioTipo.PLANO_TRABALHO: DocumentoTipoMeta(
        tipo=DocumentoOficioTipo.PLANO_TRABALHO,
        slug='plano-trabalho',
        label='Plano de trabalho',
        implemented_formats=(DocumentoFormato.DOCX, DocumentoFormato.PDF),
    ),
    DocumentoOficioTipo.ORDEM_SERVICO: DocumentoTipoMeta(
        tipo=DocumentoOficioTipo.ORDEM_SERVICO,
        slug='ordem-servico',
        label='Ordem de serviço',
        implemented_formats=(DocumentoFormato.DOCX, DocumentoFormato.PDF),
    ),
    DocumentoOficioTipo.TERMO_AUTORIZACAO: DocumentoTipoMeta(
        tipo=DocumentoOficioTipo.TERMO_AUTORIZACAO,
        slug='termo-autorizacao',
        label='Termo de autorização',
        implemented_formats=(DocumentoFormato.DOCX, DocumentoFormato.PDF),
    ),
}
_DOCUMENT_TYPE_REGISTRY_BY_SLUG = {
    meta.slug: meta for meta in _DOCUMENT_TYPE_REGISTRY.values()
}


def get_document_type_meta(tipo_documento):
    if isinstance(tipo_documento, DocumentoTipoMeta):
        return tipo_documento
    if isinstance(tipo_documento, DocumentoOficioTipo):
        return _DOCUMENT_TYPE_REGISTRY[tipo_documento]
    if isinstance(tipo_documento, str):
        normalized = (tipo_documento or '').strip()
        if normalized in _DOCUMENT_TYPE_REGISTRY_BY_SLUG:
            return _DOCUMENT_TYPE_REGISTRY_BY_SLUG[normalized]
        return _DOCUMENT_TYPE_REGISTRY[DocumentoOficioTipo(normalized)]
    raise KeyError(f'Tipo documental inválido: {tipo_documento!r}')


def iter_document_type_metas():
    return list(_DOCUMENT_TYPE_REGISTRY.values())
