from eventos.services.justificativa import get_primeira_saida_oficio

from .context import build_ordem_servico_document_context
from .renderer import get_document_template_path, render_docx_template_bytes
from .types import DocumentoOficioTipo


MESES_PTBR = {
    1: 'janeiro',
    2: 'fevereiro',
    3: 'março',
    4: 'abril',
    5: 'maio',
    6: 'junho',
    7: 'julho',
    8: 'agosto',
    9: 'setembro',
    10: 'outubro',
    11: 'novembro',
    12: 'dezembro',
}


def _get_primary_signature(context):
    return (context.get('assinaturas') or [{}])[0]


def _format_data_extenso(oficio):
    primeira_saida = get_primeira_saida_oficio(oficio)
    data_inicio = primeira_saida.date() if primeira_saida else None
    data_fim = oficio.retorno_chegada_data or oficio.retorno_saida_data or data_inicio
    if not data_inicio and not data_fim:
        return ''
    data_inicio = data_inicio or data_fim
    data_fim = data_fim or data_inicio
    if data_inicio == data_fim:
        return f'{data_inicio.day} de {MESES_PTBR.get(data_inicio.month, data_inicio.month)} de {data_inicio.year}'
    if data_inicio.year == data_fim.year and data_inicio.month == data_fim.month:
        return f'{data_inicio.day} a {data_fim.day} de {MESES_PTBR.get(data_inicio.month, data_inicio.month)} de {data_inicio.year}'
    return (
        f'{data_inicio.day} de {MESES_PTBR.get(data_inicio.month, data_inicio.month)} '
        f'a {data_fim.day} de {MESES_PTBR.get(data_fim.month, data_fim.month)} de {data_fim.year}'
    )


def _build_ordem_numero(oficio, context):
    if oficio.numero:
        return f'{int(oficio.numero):02d}'
    return context['identificacao']['numero_formatado']


def _build_equipe_deslocamento(context):
    nomes = [viajante['nome'] for viajante in context['viajantes'] if viajante['nome']]
    if not nomes:
        return 'dos servidores designados'
    if len(nomes) == 1:
        return f'do servidor {nomes[0]}'
    return f"dos servidores {', '.join(nomes)}"


def build_ordem_servico_template_context(oficio):
    context = build_ordem_servico_document_context(oficio)
    assinatura = _get_primary_signature(context)
    unidade = context['institucional']['unidade'] or context['institucional']['orgao'] or context['institucional']['sigla_orgao']
    return {
        'cargo_chefia': assinatura.get('cargo', ''),
        'data_extenso': _format_data_extenso(oficio),
        'destino': context['ordem_servico']['destinos_texto'],
        'divisao': context['institucional']['divisao'] or unidade,
        'equipe_deslocamento': _build_equipe_deslocamento(context),
        'motivo': context['ordem_servico']['finalidade'].rstrip('.'),
        'nome_chefia': assinatura.get('nome', ''),
        'ordem_de_servico': _build_ordem_numero(oficio, context),
        'sede': context['roteiro']['sede'],
        'unidade': unidade,
        'email': context['institucional']['email'],
        'endereco': context['institucional']['endereco'],
        'telefone': context['institucional'].get('telefone', ''),
        'unidade_rodape': unidade,
    }


def render_ordem_servico_docx(oficio):
    template_path = get_document_template_path(DocumentoOficioTipo.ORDEM_SERVICO)
    mapping = build_ordem_servico_template_context(oficio)
    return render_docx_template_bytes(template_path, mapping)
