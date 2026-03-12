from cadastros.models import AssinaturaConfiguracao, ConfiguracaoSistema

from eventos.models import EventoFundamentacao
from eventos.services.oficio_schema import oficio_justificativa_schema_available
from eventos.services.justificativa import (
    get_dias_antecedencia_oficio,
    get_prazo_justificativa_dias,
    get_primeira_saida_oficio,
    oficio_exige_justificativa,
    oficio_tem_justificativa,
)

from .types import DocumentoOficioTipo


EMPTY_DISPLAY = '—'


def _text_or_empty(value):
    return str(value or '').strip()


def _display(value):
    text = _text_or_empty(value)
    return text or EMPTY_DISPLAY


def _format_date_br(value):
    if not value:
        return ''
    return value.strftime('%d/%m/%Y')


def _format_time_br(value):
    if not value:
        return ''
    return value.strftime('%H:%M')


def _format_datetime_br(value):
    if not value:
        return ''
    return value.strftime('%d/%m/%Y %H:%M')


def _format_datetime_parts(date_value, time_value):
    if not date_value:
        return ''
    if time_value:
        return f'{_format_date_br(date_value)} {_format_time_br(time_value)}'.strip()
    return _format_date_br(date_value)


def _format_event_period(evento):
    if not evento or not evento.data_inicio:
        return ''
    inicio = _format_date_br(evento.data_inicio)
    fim = _format_date_br(evento.data_fim) if evento.data_fim else ''
    if fim and fim != inicio:
        return f'{inicio} a {fim}'
    return inicio


def _get_configuracao_sistema():
    return ConfiguracaoSistema.objects.order_by('pk').first()


def _build_endereco_configuracao(config):
    if not config:
        return ''
    partes = [
        _text_or_empty(config.logradouro),
        _text_or_empty(config.numero),
        _text_or_empty(config.bairro),
    ]
    cidade_uf = ' / '.join(
        [part for part in [_text_or_empty(config.cidade_endereco), _text_or_empty(config.uf)] if part]
    )
    if cidade_uf:
        partes.append(cidade_uf)
    cep = _text_or_empty(getattr(config, 'cep_formatado', '') or config.cep)
    if cep:
        partes.append(f'CEP {cep}')
    return ', '.join([parte for parte in partes if parte])


def _format_motorista_oficio(oficio):
    if oficio.motorista_oficio_numero and oficio.motorista_oficio_ano:
        return f'{int(oficio.motorista_oficio_numero):02d}/{int(oficio.motorista_oficio_ano)}'
    return _text_or_empty(oficio.motorista_oficio)


def _build_viajantes_context(oficio):
    viajantes = []
    queryset = oficio.viajantes.select_related('cargo').order_by('nome')
    for viajante in queryset:
        viajantes.append(
            {
                'nome': _text_or_empty(viajante.nome),
                'cargo': _text_or_empty(viajante.cargo.nome if getattr(viajante, 'cargo', None) else ''),
                'rg': _text_or_empty(getattr(viajante, 'rg_formatado', '') or getattr(viajante, 'rg', '')),
                'cpf': _text_or_empty(getattr(viajante, 'cpf_formatado', '') or getattr(viajante, 'cpf', '')),
            }
        )
    return viajantes


def _build_trechos_context(oficio):
    trechos = []
    destinos = []
    destinos_seen = set()
    queryset = oficio.trechos.select_related(
        'origem_estado',
        'origem_cidade',
        'destino_estado',
        'destino_cidade',
    ).order_by('ordem', 'id')
    for trecho in queryset:
        origem = _text_or_empty(
            f'{trecho.origem_cidade.nome}/{trecho.origem_estado.sigla}'
            if trecho.origem_cidade_id and trecho.origem_estado_id
            else trecho.origem_cidade or trecho.origem_estado
        )
        destino = _text_or_empty(
            f'{trecho.destino_cidade.nome}/{trecho.destino_estado.sigla}'
            if trecho.destino_cidade_id and trecho.destino_estado_id
            else trecho.destino_cidade or trecho.destino_estado
        )
        trechos.append(
            {
                'ordem': trecho.ordem + 1,
                'origem': origem,
                'destino': destino,
                'saida_data': _format_date_br(trecho.saida_data),
                'saida_hora': _format_time_br(trecho.saida_hora),
                'chegada_data': _format_date_br(trecho.chegada_data),
                'chegada_hora': _format_time_br(trecho.chegada_hora),
                'distancia_km': str(trecho.distancia_km) if trecho.distancia_km is not None else '',
                'duracao_estimada_min': trecho.duracao_estimada_min or '',
            }
        )
        if destino and destino not in destinos_seen:
            destinos_seen.add(destino)
            destinos.append(destino)
    return trechos, destinos


def _build_retorno_context(oficio):
    return {
        'origem': _text_or_empty(oficio.retorno_saida_cidade),
        'destino': _text_or_empty(oficio.retorno_chegada_cidade),
        'saida_data': _format_date_br(oficio.retorno_saida_data),
        'saida_hora': _format_time_br(oficio.retorno_saida_hora),
        'chegada_data': _format_date_br(oficio.retorno_chegada_data),
        'chegada_hora': _format_time_br(oficio.retorno_chegada_hora),
    }


def _build_roteiro_summary_lines(trechos, retorno):
    linhas = []
    for trecho in trechos:
        rota = f"{trecho['origem'] or EMPTY_DISPLAY} -> {trecho['destino'] or EMPTY_DISPLAY}"
        janela = f"Saída {trecho['saida_data']} {trecho['saida_hora']}".strip()
        chegada = f"Chegada {trecho['chegada_data']} {trecho['chegada_hora']}".strip()
        linhas.append(f'{rota} | {janela} | {chegada}')
    if retorno['origem'] or retorno['destino'] or retorno['saida_data'] or retorno['chegada_data']:
        linhas.append(
            f"Retorno {retorno['origem'] or EMPTY_DISPLAY} -> {retorno['destino'] or EMPTY_DISPLAY} | "
            f"Saída {retorno['saida_data']} {retorno['saida_hora']} | "
            f"Chegada {retorno['chegada_data']} {retorno['chegada_hora']}"
        )
    return linhas


def _build_viagem_period_context(oficio, primeira_saida, trechos):
    inicio_display = _format_datetime_br(primeira_saida)
    fim_display = _format_datetime_parts(oficio.retorno_chegada_data, oficio.retorno_chegada_hora)
    if not fim_display and trechos:
        ultimo_trecho = trechos[-1]
        fim_display = (
            f"{ultimo_trecho['chegada_data']} {ultimo_trecho['chegada_hora']}".strip()
            if ultimo_trecho['chegada_data']
            else ''
        )
    if inicio_display and fim_display:
        resumo = f'{inicio_display} a {fim_display}'
    else:
        resumo = inicio_display or fim_display
    return {
        'inicio': inicio_display,
        'fim': fim_display,
        'resumo': resumo,
    }


def _build_custeio_context(oficio):
    tipo_display = _text_or_empty(oficio.get_custeio_tipo_display() or oficio.custeio_tipo)
    instituicao = _text_or_empty(oficio.nome_instituicao_custeio)
    if oficio.custeio_tipo == oficio.CUSTEIO_OUTRA_INSTITUICAO and instituicao:
        descricao = f'{tipo_display} - {instituicao}'
    else:
        descricao = tipo_display
    return {
        'tipo': tipo_display,
        'instituicao': instituicao,
        'descricao': descricao,
    }


def _get_oficio_justificativa_texto(oficio):
    if not oficio_justificativa_schema_available():
        return ''
    return _text_or_empty(oficio.justificativa_texto)


def get_assinaturas_documento(tipo_documento):
    config = _get_configuracao_sistema()
    if not config:
        return []
    try:
        tipo = DocumentoOficioTipo(tipo_documento)
    except ValueError:
        return []
    tipos_suportados = {
        DocumentoOficioTipo.OFICIO.value,
        DocumentoOficioTipo.JUSTIFICATIVA.value,
        DocumentoOficioTipo.PLANO_TRABALHO.value,
        DocumentoOficioTipo.ORDEM_SERVICO.value,
    }
    if tipo.value not in tipos_suportados:
        return []
    assinaturas = []
    queryset = (
        AssinaturaConfiguracao.objects.filter(
            configuracao=config,
            tipo=tipo.value,
            ativo=True,
        )
        .select_related('viajante', 'viajante__cargo')
        .order_by('ordem', 'pk')
    )
    for assinatura in queryset:
        viajante = assinatura.viajante
        assinaturas.append(
            {
                'ordem': assinatura.ordem,
                'nome': _text_or_empty(viajante.nome if viajante else ''),
                'cargo': _text_or_empty(viajante.cargo.nome if viajante and getattr(viajante, 'cargo', None) else ''),
            }
        )
    return assinaturas


def _build_common_context(oficio):
    evento = oficio.evento
    config = _get_configuracao_sistema()
    trechos, destinos = _build_trechos_context(oficio)
    retorno = _build_retorno_context(oficio)
    roteiro_resumo_linhas = _build_roteiro_summary_lines(trechos, retorno)
    primeira_saida = get_primeira_saida_oficio(oficio)
    periodo_viagem = _build_viagem_period_context(oficio, primeira_saida, trechos)
    dias_antecedencia = get_dias_antecedencia_oficio(oficio)
    justificativa_required = oficio_exige_justificativa(oficio)

    motorista_nome = _text_or_empty(
        oficio.motorista_viajante.nome if oficio.motorista_viajante_id and oficio.motorista_viajante else oficio.motorista
    )
    motorista_manual = bool(not oficio.motorista_viajante_id and motorista_nome)
    destinos_texto = ', '.join(destinos)
    viajantes = _build_viajantes_context(oficio)

    return {
        'identificacao': {
            'numero_formatado': _text_or_empty(oficio.numero_formatado),
            'ano': oficio.ano or '',
            'protocolo_formatado': _text_or_empty(oficio.protocolo_formatado),
            'data_criacao_br': _format_date_br(oficio.data_criacao),
            'status': _text_or_empty(oficio.get_status_display()),
        },
        'evento': {
            'vinculado': bool(oficio.evento_id),
            'titulo': _text_or_empty(evento.titulo if evento else ''),
            'periodo': _format_event_period(evento),
        },
        'viajantes': viajantes,
        'veiculo': {
            'placa_formatada': _text_or_empty(oficio.placa_formatada),
            'modelo': _text_or_empty(oficio.modelo),
            'combustivel': _text_or_empty(oficio.combustivel),
            'tipo_viatura': _text_or_empty(oficio.get_tipo_viatura_display()),
            'porte_transporte_armas': 'Sim' if oficio.porte_transporte_armas else 'Não',
            'descricao': ' | '.join(
                [
                    part
                    for part in [
                        _text_or_empty(oficio.placa_formatada),
                        _text_or_empty(oficio.modelo),
                        _text_or_empty(oficio.get_tipo_viatura_display()),
                        _text_or_empty(oficio.combustivel),
                    ]
                    if part
                ]
            ),
        },
        'motorista': {
            'nome': motorista_nome,
            'manual': motorista_manual,
            'carona': bool(oficio.motorista_carona),
            'oficio_formatado': _format_motorista_oficio(oficio),
            'protocolo_formatado': _text_or_empty(oficio.motorista_protocolo_formatado),
            'descricao': ' | '.join(
                [
                    part
                    for part in [
                        motorista_nome,
                        'Motorista manual' if motorista_manual else '',
                        'Carona' if oficio.motorista_carona else '',
                    ]
                    if part
                ]
            ),
        },
        'roteiro': {
            'sede': _text_or_empty(
                f'{oficio.cidade_sede.nome}/{oficio.estado_sede.sigla}'
                if oficio.cidade_sede_id and oficio.estado_sede_id
                else oficio.cidade_sede or oficio.estado_sede
            ),
            'destinos': destinos,
            'destinos_texto': destinos_texto,
            'trechos': trechos,
            'retorno': retorno,
            'resumo_linhas': roteiro_resumo_linhas,
            'periodo_viagem': periodo_viagem,
        },
        'diarias': {
            'tipo_destino': _text_or_empty(oficio.get_tipo_destino_display() or oficio.tipo_destino),
            'quantidade': _text_or_empty(oficio.quantidade_diarias),
            'valor': _text_or_empty(oficio.valor_diarias),
            'valor_extenso': _text_or_empty(oficio.valor_diarias_extenso),
        },
        'custeio': _build_custeio_context(oficio),
        'conteudo': {
            'motivo': _text_or_empty(oficio.motivo),
            'justificativa_texto': _get_oficio_justificativa_texto(oficio),
        },
        'justificativa': {
            'exigida': justificativa_required,
            'preenchida': oficio_tem_justificativa(oficio),
            'prazo_minimo_dias': get_prazo_justificativa_dias(),
            'dias_antecedencia': dias_antecedencia if dias_antecedencia is not None else '',
            'primeira_saida': _format_datetime_br(primeira_saida),
        },
        'institucional': {
            'orgao': _text_or_empty(config.nome_orgao if config else ''),
            'sigla_orgao': _text_or_empty(config.sigla_orgao if config else ''),
            'divisao': _text_or_empty(config.divisao if config else ''),
            'unidade': _text_or_empty(config.unidade if config else ''),
            'endereco': _build_endereco_configuracao(config),
            'telefone': _text_or_empty(getattr(config, 'telefone_formatado', '') if config else ''),
            'email': _text_or_empty(config.email if config else ''),
        },
        'resumos': {
            'participantes_nomes': [viajante['nome'] for viajante in viajantes if viajante['nome']],
            'participantes_texto': ', '.join(viajante['nome'] for viajante in viajantes if viajante['nome']),
            'roteiro_curto': roteiro_resumo_linhas[0] if roteiro_resumo_linhas else '',
        },
    }


def build_oficio_document_context(oficio):
    context = _build_common_context(oficio)
    context.update(
        {
            'tipo_documento': DocumentoOficioTipo.OFICIO.value,
            'tipo_documento_label': 'Ofício',
            'assinaturas': get_assinaturas_documento(DocumentoOficioTipo.OFICIO.value),
        }
    )
    return context


def build_justificativa_document_context(oficio):
    context = _build_common_context(oficio)
    context.update(
        {
            'tipo_documento': DocumentoOficioTipo.JUSTIFICATIVA.value,
            'tipo_documento_label': 'Justificativa',
            'assinaturas': get_assinaturas_documento(DocumentoOficioTipo.JUSTIFICATIVA.value),
        }
    )
    return context


def build_termo_autorizacao_document_context(oficio):
    context = _build_common_context(oficio)
    context.update(
        {
            'tipo_documento': DocumentoOficioTipo.TERMO_AUTORIZACAO.value,
            'tipo_documento_label': 'Termo de autorização',
            # Regra de negócio: TERMO não exige assinatura configurada.
            'assinaturas': [],
            'termo': {
                'autorizacao_resumo': (
                    'Fica autorizado o deslocamento institucional dos servidores relacionados neste documento, '
                    'nos termos do roteiro e das condições descritas.'
                ),
                'destinos_texto': context['roteiro']['destinos_texto'],
                'periodo_viagem': context['roteiro']['periodo_viagem']['resumo'],
                'participantes_texto': context['resumos']['participantes_texto'],
            },
        }
    )
    return context


def _get_fundamentacao_texto_para_tipo(oficio, tipo_documento):
    """Retorna texto_fundamentacao do evento quando existir fundamentação do tipo indicado."""
    if not oficio.evento_id:
        return None
    try:
        fund = getattr(oficio.evento, 'fundamentacao', None)
        if fund and (fund.tipo_documento or '').strip() == tipo_documento:
            return _text_or_empty(fund.texto_fundamentacao) or None
    except Exception:
        pass
    return None


def build_plano_trabalho_document_context(oficio):
    context = _build_common_context(oficio)
    objetivo = _get_fundamentacao_texto_para_tipo(oficio, EventoFundamentacao.TIPO_PT)
    if objetivo is None:
        objetivo = context['conteudo']['motivo']
    context.update(
        {
            'tipo_documento': DocumentoOficioTipo.PLANO_TRABALHO.value,
            'tipo_documento_label': 'Plano de trabalho',
            'assinaturas': get_assinaturas_documento(DocumentoOficioTipo.PLANO_TRABALHO.value),
            'plano_trabalho': {
                'objetivo': objetivo,
                'local_periodo': (
                    ' | '.join(
                        [
                            part
                            for part in [
                                context['roteiro']['destinos_texto'] or context['roteiro']['sede'],
                                context['roteiro']['periodo_viagem']['resumo'],
                            ]
                            if part
                        ]
                    )
                ),
                'participantes_texto': context['resumos']['participantes_texto'],
                'roteiro_resumo': context['roteiro']['resumo_linhas'],
                'transporte_resumo': ' | '.join(
                    [part for part in [context['veiculo']['descricao'], context['motorista']['descricao']] if part]
                ),
                'diarias_resumo': ' | '.join(
                    [
                        part
                        for part in [
                            context['diarias']['tipo_destino'],
                            f"{context['diarias']['quantidade']} diária(s)" if context['diarias']['quantidade'] else '',
                            context['diarias']['valor'],
                        ]
                        if part
                    ]
                ),
                'custeio_resumo': context['custeio']['descricao'],
            },
        }
    )
    return context


def build_ordem_servico_document_context(oficio):
    context = _build_common_context(oficio)
    finalidade = _get_fundamentacao_texto_para_tipo(oficio, EventoFundamentacao.TIPO_OS)
    if finalidade is None:
        finalidade = context['conteudo']['motivo']
    context.update(
        {
            'tipo_documento': DocumentoOficioTipo.ORDEM_SERVICO.value,
            'tipo_documento_label': 'Ordem de serviço',
            'assinaturas': get_assinaturas_documento(DocumentoOficioTipo.ORDEM_SERVICO.value),
            'ordem_servico': {
                'finalidade': finalidade,
                'destinos_texto': context['roteiro']['destinos_texto'],
                'periodo_viagem': context['roteiro']['periodo_viagem']['resumo'],
                'participantes_texto': context['resumos']['participantes_texto'],
                'transporte_resumo': ' | '.join(
                    [part for part in [context['veiculo']['descricao'], context['motorista']['nome']] if part]
                ),
            },
        }
    )
    return context
