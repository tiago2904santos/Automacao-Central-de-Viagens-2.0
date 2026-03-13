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
    titulo = (
        f"PLANO DE TRABALHO Nº {context.get('numero_plano_trabalho') or '—'} - "
        f"OFÍCIO Nº {context['identificacao']['numero_formatado'] or 'RASCUNHO'}"
    )
    subtitulo = context['institucional']['orgao'] or context['institucional']['sigla_orgao']
    document = create_base_document(titulo, subtitulo)

    add_section_heading(document, 'Dados gerais')
    add_label_value(document, 'Número do plano', context.get('numero_plano_trabalho', ''))
    add_label_value(document, 'Título', context['plano_trabalho'].get('titulo', ''))
    add_label_value(document, 'Contexto', context['plano_trabalho'].get('contexto', ''))
    add_label_value(document, 'Evento', context['evento']['titulo'])
    add_label_value(document, 'Protocolo', context['identificacao']['protocolo_formatado'])
    add_label_value(document, 'Período', context.get('periodo_execucao') or context['roteiro']['periodo_viagem']['resumo'])
    add_label_value(document, 'Destino(s)', context.get('destino') or context['roteiro']['destinos_texto'])
    add_label_value(document, 'Solicitante', context['plano_trabalho'].get('solicitante', ''))
    add_label_value(document, 'Município / local', context.get('local_execucao', ''))
    add_label_value(document, 'Horário de atendimento', context.get('horario_atendimento', ''))
    add_label_value(document, 'Dias do evento (extenso)', context.get('dias_evento_extenso', ''))
    add_multiline_value(document, 'Objetivo / finalidade', context['plano_trabalho']['objetivo'])

    add_section_heading(document, 'Coordenação e equipe')
    if context.get('coordenacao_formatada'):
        add_multiline_value(document, 'Coordenação', context['coordenacao_formatada'])
    add_label_value(document, 'Efetivo previsto', context.get('quantidade_de_servidores', ''))
    add_label_value(document, 'Composição da equipe', context['plano_trabalho'].get('efetivo_resumo', ''))

    add_section_heading(document, 'Atividades')
    if context.get('atividades_formatada'):
        add_multiline_value(document, 'Atividades', context['atividades_formatada'])
    if context.get('metas_formatada'):
        add_multiline_value(document, 'Metas', context['metas_formatada'])
    if context.get('unidade_movel'):
        add_label_value(document, 'Unidade móvel', context['unidade_movel'])

    add_section_heading(document, 'Estrutura operacional')
    add_multiline_value(document, 'Locais', context['plano_trabalho'].get('locais', ''))
    add_multiline_value(document, 'Cronograma', context['plano_trabalho'].get('cronograma', ''))
    add_multiline_value(document, 'Materiais / equipamentos', context['plano_trabalho'].get('materiais_equipamentos', ''))
    add_multiline_value(document, 'Recursos adicionais', context['plano_trabalho'].get('recursos', ''))
    if context['plano_trabalho'].get('observacoes_operacionais'):
        add_multiline_value(document, 'Observações operacionais', context['plano_trabalho']['observacoes_operacionais'])

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
    add_label_value(document, 'Composição (diárias)', context.get('diarias_x') or context['plano_trabalho']['diarias_resumo'])
    add_label_value(document, 'Valor unitário (1 servidor)', context.get('valor_unitario', ''))
    add_label_value(document, 'Valor unitário por extenso', context.get('valor_unitario_por_extenso', ''))
    add_label_value(document, 'Valor total', context.get('valor_total', '') or context['diarias']['valor'])
    add_label_value(document, 'Valor total por extenso', context.get('valor_total_por_extenso') or context['diarias']['valor_extenso'])
    add_label_value(document, 'Custeio', context['plano_trabalho']['custeio_resumo'])

    add_section_heading(document, 'Informações institucionais')
    add_label_value(document, 'Data (extenso)', context.get('data_extenso', ''))
    add_label_value(document, 'Órgão', context['institucional']['orgao'] or context['institucional']['sigla_orgao'])
    add_label_value(document, 'Unidade', context['institucional']['unidade'])
    add_label_value(document, 'Divisão', context['institucional']['divisao'])
    add_label_value(document, 'Sede', context['institucional'].get('sede', ''))
    add_label_value(document, 'Endereço', context['institucional']['endereco'])
    add_label_value(document, 'Nome da chefia', context['institucional'].get('nome_chefia', ''))
    add_label_value(document, 'Cargo da chefia', context['institucional'].get('cargo_chefia', ''))

    if context['justificativa']['exigida'] and context['conteudo']['justificativa_texto']:
        add_multiline_value(document, 'Justificativa registrada', context['conteudo']['justificativa_texto'])

    add_signature_blocks(document, context['assinaturas'])
    return document_to_bytes(document)
