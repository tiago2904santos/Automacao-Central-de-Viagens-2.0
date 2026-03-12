from .context import (
    build_justificativa_document_context,
    build_oficio_document_context,
    build_ordem_servico_document_context,
    build_plano_trabalho_document_context,
    build_termo_autorizacao_document_context,
    get_assinaturas_documento,
)
from .backends import (
    get_document_backend_capabilities,
    get_docx_backend_availability,
    get_pdf_backend_availability,
    reset_document_backend_capabilities_cache,
)
from .filenames import build_document_filename
from .types import (
    DocumentoFormato,
    DocumentoOficioTipo,
    DocumentFormatNotAvailable,
    DocumentGenerationError,
    DocumentRendererUnavailable,
    DocumentTemplateUnavailable,
    DocumentTypeNotImplemented,
    DocumentValidationError,
    get_document_type_meta,
    iter_document_type_metas,
)
from .validators import (
    get_document_generation_status,
    validate_oficio_for_document_generation,
)


def render_document_bytes(*args, **kwargs):
    from .renderer import render_document_bytes as _render_document_bytes

    return _render_document_bytes(*args, **kwargs)

__all__ = [
    'DocumentoFormato',
    'DocumentoOficioTipo',
    'DocumentFormatNotAvailable',
    'DocumentGenerationError',
    'DocumentRendererUnavailable',
    'DocumentTemplateUnavailable',
    'DocumentTypeNotImplemented',
    'DocumentValidationError',
    'build_document_filename',
    'build_justificativa_document_context',
    'build_oficio_document_context',
    'build_ordem_servico_document_context',
    'build_plano_trabalho_document_context',
    'build_termo_autorizacao_document_context',
    'get_document_backend_capabilities',
    'get_docx_backend_availability',
    'get_pdf_backend_availability',
    'get_assinaturas_documento',
    'get_document_generation_status',
    'get_document_type_meta',
    'iter_document_type_metas',
    'render_document_bytes',
    'reset_document_backend_capabilities_cache',
    'validate_oficio_for_document_generation',
]
