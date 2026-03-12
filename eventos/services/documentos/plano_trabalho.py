from .context import build_plano_trabalho_document_context
from .renderer import (
    add_bullet_list,
    add_label_value,
    add_multiline_value,
    add_section_heading,
    add_signature_blocks,
    add_simple_table,
    create_base_document,
    document_to_bytes,
)


def render_plano_trabalho_docx(oficio):
    context = build_plano_trabalho_document_context(oficio)
    titulo = f"PLANO DE TRABALHO - OFÍCIO Nº {context['identificacao']['numero_formatado'] or 'RASCUNHO'}"
    subtitulo = context['institucional']['orgao'] or context['institucional']['sigla_orgao']
    document = create_base_document(titulo, subtitulo)

    add_section_heading(document, 'Identificação')
    add_label_value(document, 'Evento', context['evento']['titulo'])
    add_label_value(document, 'Protocolo', context['identificacao']['protocolo_formatado'])
    add_label_value(document, 'Período da viagem', context['roteiro']['periodo_viagem']['resumo'])
    add_label_value(document, 'Destino(s)', context['roteiro']['destinos_texto'])

    add_multiline_value(document, 'Objetivo / finalidade', context['plano_trabalho']['objetivo'])
    add_label_value(document, 'Local e período', context['plano_trabalho']['local_periodo'])

    participantes_rows = [
        [viajante['nome'], viajante['cargo'], viajante['rg'], viajante['cpf']]
        for viajante in context['viajantes']
    ]
    if participantes_rows:
        add_section_heading(document, 'Participantes / servidores')
        add_simple_table(document, ['Nome', 'Cargo', 'RG', 'CPF'], participantes_rows)

    add_bullet_list(
        document,
        'Roteiro resumido',
        context['plano_trabalho']['roteiro_resumo'],
        empty_text='Roteiro ainda não informado.',
    )

    add_section_heading(document, 'Transporte')
    add_label_value(document, 'Veículo', context['veiculo']['descricao'])
    add_label_value(document, 'Motorista', context['motorista']['descricao'])
    add_label_value(document, 'Sede', context['roteiro']['sede'])

    add_section_heading(document, 'Diárias e custeio')
    add_label_value(document, 'Resumo das diárias', context['plano_trabalho']['diarias_resumo'])
    add_label_value(document, 'Valor por extenso', context['diarias']['valor_extenso'])
    add_label_value(document, 'Custeio', context['plano_trabalho']['custeio_resumo'])

    add_section_heading(document, 'Informações institucionais')
    add_label_value(document, 'Órgão', context['institucional']['orgao'] or context['institucional']['sigla_orgao'])
    add_label_value(document, 'Unidade', context['institucional']['unidade'])
    add_label_value(document, 'Divisão', context['institucional']['divisao'])
    add_label_value(document, 'Endereço', context['institucional']['endereco'])

    if context['justificativa']['exigida'] and context['conteudo']['justificativa_texto']:
        add_multiline_value(document, 'Justificativa registrada', context['conteudo']['justificativa_texto'])

    add_signature_blocks(document, context['assinaturas'])
    return document_to_bytes(document)
