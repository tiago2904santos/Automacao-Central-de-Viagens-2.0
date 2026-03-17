# LIVRO DE FUNCOES E REGRAS DE NEGOCIO - CADASTRO DE OFICIOS (LEGADO MAPEADO NO PROJETO)

Data da auditoria: 17/03/2026  
Branch: docs/livro-oficios

## 1. Visao geral do modulo de oficios

O cadastro de oficios foi identificado como um fluxo wizard de 4 passos, com tela adicional de justificativa e tela de documentos, operando com status RASCUNHO/FINALIZADO e com possibilidade de vinculo a evento (origem EVENTO) ou avulso (origem AVULSO).

Arquitetura operacional mapeada:
- Dominio principal: `Oficio` e `OficioTrecho`.
- Entrada de dados: wizard (`step1`, `step2`, `step3`, `step4`) + justificativa.
- Persistencia: model `Oficio` com M2M de viajantes e FK para evento/veiculo/motorista/roteiro.
- Regras criticas: protocolo, custeio, carona de motorista, validacao para finalizacao, justificativa por antecedencia, diarias.
- Saidas: central de documentos por ofici o (DOCX/PDF quando disponivel), lista global de oficios com cards de status documental.
- Front-end: header sticky, stepper, quick report lateral fixo em desktop, autosave por XHR + pagehide beacon, autocomplete de viajantes/motoristas, lookup de viatura por placa.

Escopo auditado nesta rodada:
- Rotas, views, forms, models, templates, JS, CSS, services, validators, context builders, utilitarios e pontos de integracao que impactam o cadastro de oficios.
- Fluxos de oficios no hub do evento (Etapa 5), lista global, exclusao, justificativa e documentos.

---

## 2. Mapa completo das telas/etapas

### 2.1 Rotas principais do modulo

Origem: `eventos/urls.py`

- `oficio/novo/` -> `oficio_novo`
- `oficio/<pk>/editar/` -> `oficio_editar`
- `oficio/<pk>/excluir/` -> `oficio_excluir`
- `oficio/<pk>/step1/` -> `oficio_step1`
- `oficio/step1/viajantes/` -> `oficio_step1_viajantes_api`
- `oficio/step2/motoristas/` -> `oficio_step2_motoristas_api`
- `oficio/step2/veiculos/` -> `oficio_step2_veiculos_busca_api`
- `oficio/step2/veiculo/` -> `oficio_step2_veiculo_api`
- `oficio/<pk>/step2/` -> `oficio_step2`
- `oficio/<pk>/step3/` -> `oficio_step3`
- `oficio/<pk>/step3/calcular-diarias/` -> `oficio_step3_calcular_diarias`
- `oficio/<pk>/justificativa/` -> `oficio_justificativa`
- `oficio/<pk>/documentos/` -> `oficio_documentos`
- `oficio/<pk>/documentos/<tipo_documento>/<formato>/` -> `oficio_documento_download`
- `oficio/<pk>/step4/` -> `oficio_step4`

Rotas de integracao com fluxo guiado do evento:
- `<evento_id>/guiado/etapa-5/` -> lista de oficios do evento (`guiado_etapa_3`)
- `<evento_id>/guiado/etapa-5/criar-oficio/` -> cria rascunho e abre wizard (`guiado_etapa_3_criar_oficio`)

Rotas globais relacionadas:
- `oficios/` -> `oficio_global_lista` (listagem global)

### 2.2 Tela de hub de oficios no evento (Etapa 5)

- Rota: `<evento_id>/guiado/etapa-5/`
- View: `guiado_etapa_3`
- Template: `templates/eventos/guiado/etapa_3.html`
- Acoes:
  - Criar oficio no evento (POST para etapa-5/criar-oficio)
  - Editar (abre wizard step1)
  - Abrir justificativa
  - Abrir documentos
  - Excluir
  - Navegar para painel / etapa 4 / etapa 6
- Dados exibidos:
  - numero/ano, protocolo, destino/tipo, status, status justificativa
- Pre-condicao:
  - evento valido
- Efeito colateral:
  - nenhum em GET; criacao delegada em POST

### 2.3 Step 1 - Dados e viajantes

- Rota: `oficio/<pk>/step1/`
- View: `oficio_step1`
- Template: `templates/eventos/oficio/wizard_step1.html`
- Form: `OficioStep1Form`
- JS:
  - `static/js/oficio_wizard.js` (autosave + layout)
  - JS inline do template (autocomplete viajantes, chips, preview, custeio dinamico, modelo de motivo)
- CSS relevante:
  - `.oficio-wizard-header`, `.oficio-stepper`, `.oficio-quick-report`, `.oficio-wizard-layout`
- Campos:
  - `oficio_numero` (readonly)
  - `protocolo` (obrigatorio + mascara)
  - `data_criacao` (readonly)
  - `modelo_motivo`
  - `motivo`
  - `custeio_tipo` (obrigatorio)
  - `nome_instituicao_custeio` (condicional)
  - `viajantes` (obrigatorio no clean)
- Botoes/acoes:
  - salvar
  - salvar e continuar
  - salvar motivo atual como novo modelo
  - gerenciar modelos de motivo
  - cadastrar novo viajante
- Regras:
  - protocolo com 9 digitos canonicos
  - ao menos 1 viajante
  - custeio OUTRA_INSTITUICAO exige instituicao
  - custeio diferente de OUTRA_INSTITUICAO limpa nome instituicao
  - motivo pode ser preenchido por modelo
- Efeitos ao salvar:
  - atualiza campos step1 no model
  - seta viajantes M2M
  - sincroniza participantes do evento quando oficio vinculado
  - opcionalmente cria novo `ModeloMotivoViagem`

### 2.4 Step 2 - Transporte

- Rota: `oficio/<pk>/step2/`
- View: `oficio_step2`
- Template: `templates/eventos/oficio/wizard_step2.html`
- Form: `OficioStep2Form` (form moderno), existe `LegacyOficioStep2Form` legado auxiliar
- APIs auxiliares:
  - `oficio_step2_motoristas_api`
  - `oficio_step2_veiculos_busca_api`
  - `oficio_step2_veiculo_api`
- JS:
  - `static/js/oficio_wizard.js`
  - JS inline do template (modo motorista manual/servidor, carona, autocomplete, lookup de placa)
  - mascara protocolo/placa via `static/js/masks.js`
- Campos:
  - veiculo: `placa`, `modelo`, `combustivel`, `tipo_viatura`, `porte_transporte_armas`
  - motorista: `motorista_viajante` (hidden + autocomplete), `motorista_nome` (manual), `motorista_oficio_numero`, `motorista_oficio_ano`, `motorista_protocolo`
- Regras:
  - placa/modelo/combustivel obrigatorios
  - motorista sem cadastro ou fora dos viajantes => carona
  - carona exige oficio numero/ano e protocolo motorista
  - protocolo motorista com 9 digitos (normalizado)
  - lookup por placa pode autopreencher modelo/combustivel/tipo_viatura
  - tenta preencher `carona_oficio_referencia` por numero/ano
- Efeitos ao salvar:
  - persiste composicao de transporte e motorista
  - atualiza FK `veiculo`, `motorista_viajante`, campos texto e flags

### 2.5 Step 3 - Roteiro e diarias

- Rota: `oficio/<pk>/step3/`
- View: `oficio_step3`
- Template: `templates/eventos/oficio/wizard_step3.html`
- Endpoint de calculo:
  - `oficio/<pk>/step3/calcular-diarias/` -> `oficio_step3_calcular_diarias`
- JS:
  - `static/js/oficio_wizard.js`
  - JS inline de alto volume para estado do roteiro, destinos, trechos, retorno, estimativas e diarias
- Campos/estado:
  - modo roteiro: EVENTO_EXISTENTE ou ROTEIRO_PROPRIO
  - sede (estado/cidade)
  - destinos
  - trechos de ida
  - retorno (saida/chegada, distancia, tempos)
  - totais de diarias (`tipo_destino`, `quantidade_diarias`, `valor_diarias`, `valor_diarias_extenso`)
- Regras:
  - valida estrutura de roteiro e retorno antes de calcular diarias
  - pode reutilizar/salvar roteiro para nao duplicar
  - gera/atualiza `OficioTrecho`
  - calcula tipo de destino e diarias por periodizacao
- Efeitos ao salvar:
  - persiste sede, tipo destino, retorno, campos de diarias
  - persiste/atualiza trechos
  - associa `roteiro_evento` quando aplicavel

### 2.6 Tela de justificativa do oficio

- Rota: `oficio/<pk>/justificativa/`
- View: `oficio_justificativa`
- Template: `templates/eventos/oficio/justificativa.html`
- Form: `OficioJustificativaForm`
- JS:
  - autosave
  - aplicar modelo de justificativa por API
  - contador de caracteres
- Campos:
  - `modelo_justificativa`
  - `justificativa_texto`
- Regras:
  - depende de disponibilidade de schema da justificativa (`oficio_schema`)
  - texto final e persistido no oficio
- Efeito colateral:
  - atualiza `justificativa_modelo` e `justificativa_texto`

### 2.7 Step 4 - Resumo/finalizacao

- Rota: `oficio/<pk>/step4/`
- View: `oficio_step4`
- Template: `templates/eventos/oficio/wizard_step4.html`
- Blocos exibidos:
  - dados/viajantes
  - transporte
  - roteiro/diarias
  - justificativa
  - finalizacao
- Acoes:
  - salvar oficio (sem finalizar)
  - marcar gerar termo preenchido (sim/nao)
  - baixar documento(s) disponiveis
  - editar justificativa
  - finalizar oficio
- Regras de finalizacao:
  - valida `step1`, `step2`, `step3` e justificativa (quando obrigatoria)
  - se apenas justificativa pendente: redireciona para tela justificativa
  - se houver outras pendencias: renderiza erros por secao
- Efeito colateral:
  - status passa para FINALIZADO
  - mensagens e links de termo quando habilitado

### 2.8 Tela de documentos do oficio

- Rota: `oficio/<pk>/documentos/`
- View: `oficio_documentos`
- Template: `templates/eventos/oficio/documentos.html`
- Download:
  - `oficio_documento_download` (DOCX/PDF)
- Conteudo:
  - cards de documentos principais e complementares
  - status por formato e indisponibilidades de backend/template/validacao

### 2.9 Tela de exclusao

- Rota: `oficio/<pk>/excluir/`
- View: `oficio_excluir`
- Template: `templates/eventos/oficio/excluir_confirm.html`
- Regras:
  - bloqueia exclusao se evento finalizado
- Mensagem de negocio:
  - numero do oficio fica livre para reutilizacao no ano

### 2.10 Lista global de oficios

- Rota: `oficios/`
- View: `oficio_global_lista`
- Template: `templates/eventos/global/oficios_lista.html`
- Filtros:
  - busca ampla, evento, status, ano, numero, protocolo, destino
- Acoes por card:
  - abrir wizard
  - excluir
  - acoes por documento (editar/baixar)

---

## 3. Inventario de arquivos envolvidos

### 3.1 Back-end principal

- `eventos/urls.py`
- `eventos/views.py`
- `eventos/views_global.py`
- `eventos/forms.py`
- `eventos/models.py`
- `eventos/utils.py`

### 3.2 Servicos de regras de negocio

- `eventos/services/diarias.py`
- `eventos/services/justificativa.py`
- `eventos/services/oficio_schema.py`
- `eventos/services/estimativa_local.py` (estimativas de trecho/retorno)
- `eventos/services/routing_provider.py` (provider de rota quando aplicavel)

### 3.3 Servicos documentais

- `eventos/services/documentos/types.py`
- `eventos/services/documentos/validators.py`
- `eventos/services/documentos/context.py`
- `eventos/services/documentos/renderer.py`
- `eventos/services/documentos/oficio.py`
- `eventos/services/documentos/justificativa.py`
- `eventos/services/documentos/termo_autorizacao.py`
- `eventos/services/documentos/plano_trabalho.py`
- `eventos/services/documentos/ordem_servico.py`
- `eventos/services/documentos/backends.py`
- `eventos/services/documentos/filenames.py`

### 3.4 Templates de oficio e fluxo

- `templates/eventos/oficio/wizard_step1.html`
- `templates/eventos/oficio/wizard_step2.html`
- `templates/eventos/oficio/wizard_step3.html`
- `templates/eventos/oficio/wizard_step4.html`
- `templates/eventos/oficio/justificativa.html`
- `templates/eventos/oficio/documentos.html`
- `templates/eventos/oficio/excluir_confirm.html`
- `templates/eventos/oficio/_wizard_header.html`
- `templates/eventos/oficio/_wizard_stepper.html`
- `templates/eventos/guiado/etapa_3.html`
- `templates/eventos/global/oficios_lista.html`

### 3.5 Front-end compartilhado

- `static/js/oficio_wizard.js`
- `static/js/masks.js`
- `static/css/style.css`

### 3.6 Templates/Forms globais com dependencia de oficio

- `templates/eventos/global/documento_avulso_form.html`
- `eventos/forms.py` (`DocumentoAvulsoForm` com campo FK `oficio`)
- `eventos/views_global.py` (documentos avulsos vinculaveis a oficio)

### 3.7 Assets documentais

- `eventos/resources/documentos/oficio_model.docx`

---

## 4. Inventario de funcoes e metodos

Observacao: inventario absoluto focado no fluxo de cadastro de oficios e seus subfluxos documentais/diarias/justificativa.

### 4.1 Views e helpers do wizard (`eventos/views.py`)

Funcoes de entrada (views):
- `guiado_etapa_3(evento_id)`
- `guiado_etapa_3_criar_oficio(evento_id)`
- `oficio_novo()`
- `oficio_editar(pk)`
- `oficio_excluir(pk)`
- `oficio_step1(pk)`
- `oficio_step1_viajantes_api()`
- `oficio_step2(pk)`
- `oficio_step2_motoristas_api()`
- `oficio_step2_veiculos_busca_api()`
- `oficio_step2_veiculo_api()`
- `oficio_step3(pk)`
- `oficio_step3_calcular_diarias(pk)`
- `oficio_justificativa(pk)`
- `oficio_step4(pk)`
- `oficio_documentos(pk)`
- `oficio_documento_download(pk, tipo_documento, formato)`

Helpers de orquestracao do oficio:
- `_get_oficio_or_404_for_user`
- `_save_oficio_preserving_status`
- `_oficio_redirect_pos_exclusao`
- `_bloquear_edicao_oficio_se_evento_finalizado`
- `_is_autosave_request`
- `_autosave_success_response`

Helpers de navegacao/UI do wizard:
- `_build_oficio_wizard_steps`
- `_apply_oficio_wizard_context`
- `_oficio_justificativa_url`

Helpers de Step 1:
- `_build_oficio_step1_initial`
- `_build_oficio_step1_preview`
- `_autosave_oficio_step1`
- `_viajantes_step1_ids_para_contexto`
- `_normalizar_ids_inteiros`
- `_carregar_viajantes_por_ids`
- `_serializar_viajante_oficio`
- `_build_custeio_preview_text`

Helpers de Step 2:
- `_build_oficio_step2_initial`
- `_build_step2_preview_data`
- `_autosave_oficio_step2`
- `_build_motorista_preview_data`
- `_step2_field_value`
- `_step2_normalize_display`

Helpers de Step 3 (estado, validacao, persistencia):
- `_build_step3_empty_state`
- `_build_step3_state_from_post`
- `_build_step3_state_from_estrutura`
- `_build_step3_state_from_roteiro_evento`
- `_build_step3_route_options`
- `_get_oficio_step3_saved_state`
- `_get_oficio_step3_seed_state`
- `_serialize_step3_state`
- `_autosave_oficio_step3`
- `_validate_step3_state`
- `_salvar_step3_oficio`
- `_ensure_reusable_step3_route`
- `_salvar_roteiro_reutilizavel_oficio`
- `_apply_saved_route_reference_to_step3`
- `_build_step3_trechos_para_roteiro`
- `_build_step3_signature_from_state`
- `_build_step3_signature_from_roteiro`
- `_build_step3_diarias_fallback`
- `_calculate_step3_diarias_from_state`
- `_normalize_step3_state_destinos_para_parana`
- `_step3_format_date_time_br`
- `_step3_format_minutes`

Helpers de justificativa/finalizacao/documentos:
- `_build_oficio_justificativa_info`
- `_validate_oficio_for_finalize`
- `_build_oficio_step4_context`
- `_autosave_oficio_step4`
- `_parse_step4_termo_choice`
- `_autosave_oficio_justificativa`
- `_build_oficio_justificativa_context`
- `_build_oficio_documentos_context`
- `_build_oficio_document_download_context`
- `_build_oficio_termo_autorizacao_context`
- `_download_oficio_documento`

Quick report:
- `_build_oficio_quick_report_data`
- `_build_oficio_responsavel_label`
- `_build_step3_periodo_display_from_state`
- `_build_step3_destino_principal_from_state`

Classificacao por criticidade para portabilidade:
- Criticas (portar 1:1): validacoes de step, finalizacao, protocolo, carona, diarias, persistencia step3, justificativa.
- Acessorias (pode adaptar): quick report, ordenacao visual, mensagens de UX, detalhes de cards globais.

Dependencia de evento por funcao:
- Dependem de evento: `guiado_etapa_3*`, sincronizacao de participantes, blocos de fundamentacao/responsavel.
- Nao dependem estritamente: wizard steps em oficio avulso (`oficio_novo` sem `evento_id`, step1-4, justificativa, documentos).

### 4.2 Forms (`eventos/forms.py`)

Forms diretamente ligados a oficios:
- `OficioStep1Form`
  - `clean_protocolo`, `clean`, `__init__`
- `LegacyOficioStep2Form`
  - `clean_motorista_protocolo`, `clean`, `__init__`
- `OficioStep2Form`
  - `clean_placa`, `clean_modelo`, `clean_combustivel`, `clean_motorista_nome`, `clean_motorista_viajante`, `clean_motorista_protocolo`, `clean`, `__init__`
  - helpers internos: `_build_motorista_choice_payloads`, `_build_motorista_choices`, `_build_selected_motorista_payload`, `_raw_motorista_value`, `_raw_motorista_nome`, `_resolve_manual_selected`, `_resolve_carona_preview`, `_resolve_motorista_oficio_ano_display`
- `OficioJustificativaForm`
  - `clean_justificativa_texto`, `clean`, `__init__`

Forms de dependencia indireta:
- `ModeloMotivoViagemForm`
- `ModeloJustificativaForm`
- `DocumentoAvulsoForm` (campo `oficio`, vinculos e placeholders)

### 4.3 Models (`eventos/models.py`)

Model principal:
- `Oficio`
  - metodos/propriedades: `__str__`, `numero_formatado`, `normalize_digits`, `normalize_protocolo`, `format_protocolo`, `protocolo_formatado`, `get_next_available_numero`, `motorista_protocolo_formatado`, `placa_formatada`, `motorista_oficio_formatado`, `retorno_tempo_total_final_min`, `clean`, `save`, `data_criacao_formatada_br`

Model de trechos:
- `OficioTrecho`
  - `__str__`, `tempo_total_final_min`

### 4.4 Views globais (`eventos/views_global.py`) que afetam oficios

- `oficio_global_lista`
- `_build_oficio_filters`
- `_oficio_destinos_display`
- `_oficio_periodo_display`
- `_oficio_viajantes_display`
- `_oficio_process_status_meta`
- `_build_oficio_document_actions`
- `_build_oficio_document_cards`
- `documentos_hub`
- `documento_avulso_novo`
- `documento_avulso_editar`
- `documento_avulso_download`

### 4.5 Utils (`eventos/utils.py`)

- `mapear_tipo_viatura_para_oficio`
- `buscar_veiculo_finalizado_por_placa`
- `buscar_veiculos_finalizados`
- `serializar_veiculo_para_oficio`
- `hhmm_to_minutes` e `minutes_to_hhmm` (tempo no fluxo)

### 4.6 Services de negocio

`eventos/services/justificativa.py`:
- `get_prazo_justificativa_dias`
- `get_primeira_saida_oficio`
- `get_dias_antecedencia_oficio`
- `oficio_exige_justificativa`
- `oficio_tem_justificativa`

`eventos/services/diarias.py`:
- `classify`, `infer_tipo_destino_from_paradas`, `count_pernoites`, `build_periods`, `calculate_periodized_diarias`, `valor_por_extenso_ptbr`, etc.

`eventos/services/oficio_schema.py`:
- `get_oficio_justificativa_schema_status`, `oficio_justificativa_schema_available`

### 4.7 Services documentais de oficio

Contexto e validacao:
- `build_oficio_document_context`
- `build_justificativa_document_context`
- `build_termo_autorizacao_document_context`
- `build_plano_trabalho_document_context`
- `build_ordem_servico_document_context`
- `validate_oficio_for_document_generation`
- `get_document_generation_status`

Renderizacao:
- `render_oficio_docx`
- `render_justificativa_docx`
- `render_termo_autorizacao_docx`
- `render_plano_trabalho_docx`
- `render_ordem_servico_docx`
- `render_document_bytes`

Backends/infra:
- `get_docx_backend_availability`
- `get_pdf_backend_availability`
- `get_document_backend_availability`
- `get_document_template_path`
- `get_document_template_availability`

### 4.8 JS do fluxo

`static/js/oficio_wizard.js`:
- `bindStickyLayout`
- `setStickyHeaderOffset`
- `syncQuickReportLayout`
- `createAutosave` (schedule/flush/beacon)

`static/js/masks.js`:
- `formatProtocolo`, `formatPlaca`, normalizadores e aplicacao de mascara por `data-mask`

---

## 5. Inventario de forms e campos

### 5.1 Campos persistidos em `Oficio`

Identificacao e origem:
- `evento` (FK, opcional)
- `tipo_origem` (AVULSO/EVENTO)
- `numero`, `ano` (unicos por ano)
- `status` (RASCUNHO/FINALIZADO)
- `protocolo`
- `data_criacao`

Step 1:
- `modelo_motivo` (FK)
- `motivo`
- `custeio_tipo`
- `nome_instituicao_custeio`
- `viajantes` (M2M)

Step 2:
- `veiculo` (FK)
- `placa`, `modelo`, `combustivel`, `tipo_viatura`, `porte_transporte_armas`
- `motorista_viajante` (FK)
- `motorista` (nome)
- `motorista_carona`
- `motorista_oficio`, `motorista_oficio_numero`, `motorista_oficio_ano`
- `motorista_protocolo`
- `carona_oficio_referencia` (FK auto)

Step 3:
- `roteiro_modo`, `roteiro_evento` (FK)
- `estado_sede`, `cidade_sede`
- `tipo_destino`
- retorno: `retorno_saida_cidade`, `retorno_saida_data`, `retorno_saida_hora`, `retorno_chegada_cidade`, `retorno_chegada_data`, `retorno_chegada_hora`, `retorno_distancia_km`, `retorno_duracao_estimada_min`, `retorno_tempo_cru_estimado_min`, `retorno_tempo_adicional_min`, `retorno_rota_fonte`, `retorno_rota_calculada_em`
- diarias: `quantidade_diarias`, `valor_diarias`, `valor_diarias_extenso`

Step 4 / justificativa:
- `justificativa_modelo` (FK)
- `justificativa_texto`
- `gerar_termo_preenchido`

### 5.2 Campos persistidos em `OficioTrecho`

- `oficio`, `ordem`
- origem: `origem_estado`, `origem_cidade`
- destino: `destino_estado`, `destino_cidade`
- datas/horas: `saida_data`, `saida_hora`, `chegada_data`, `chegada_hora`
- rota: `distancia_km`, `duracao_estimada_min`, `tempo_cru_estimado_min`, `tempo_adicional_min`, `rota_fonte`, `rota_calculada_em`

### 5.3 Campos de interface (nao persistidos diretamente)

- `oficio_numero` (display readonly no Step 1)
- chips de viajantes selecionados
- `motorista_viajante` no form moderno (hidden + payload autocomplete)
- `motorista_oficio_ano_display` (display)
- campos de preview/quick report
- inputs temporarios de Step 3 em JSON (estado local de roteiro)

### 5.4 Obrigatoriedade por etapa

Step 1:
- obrigatorios: protocolo, custeio_tipo, pelo menos 1 viajante
- condicional: nome instituicao quando OUTRA_INSTITUICAO

Step 2:
- obrigatorios: placa, modelo, combustivel
- condicional carona: motorista_oficio_numero, motorista_oficio_ano, motorista_protocolo
- motorista: servidor selecionado ou nome manual

Step 3:
- obrigatorios para finalizar: step3 salvo, trechos validos, retorno valido, tipo_destino, diarias calculadas

Justificativa:
- obrigatoria apenas quando antecedencia < prazo configurado

### 5.5 Defaults e mascaras

Defaults:
- `custeio_tipo`: UNIDADE
- `tipo_viatura`: DESCARACTERIZADA
- `motorista_oficio_ano`: ano atual
- `porte_transporte_armas`: true

Mascaras:
- protocolo: `XX.XXX.XXX-X`
- placa: formato antigo/mercosul
- cpf/rg/telefone/cep (shared)

### 5.6 Participacao em preview/resumo/exportacao

- Preview quick report: dados de Step1/2/3 + justificativa + diarias.
- Resumo final (Step4): render consolidado para validacao humana.
- Exportacao documental: usa contexto composto do oficio, trechos, retorno, viajantes, assinaturas e configuracoes.

---

## 6. Inventario de regras de negocio

### 6.1 Numeracao e protocolo

1) Regra: numeracao anual por menor lacuna disponivel  
- Onde: `Oficio.get_next_available_numero`, `Oficio.save`  
- Disparo: criacao de oficio sem `numero`  
- Efeito: define `numero` e `ano` automaticamente  
- Portar no novo: sim, 1:1

2) Regra: protocolo canonico de 9 digitos  
- Onde: `Oficio.clean/save`, `OficioStep1Form.clean_protocolo`  
- Disparo: salvar step1/model  
- Mensagem: formato `XX.XXX.XXX-X`  
- Portar: sim, 1:1

3) Regra: protocolo motorista com 9 digitos quando carona  
- Onde: `Oficio.clean/save`, `OficioStep2Form.clean_motorista_protocolo/clean`  
- Disparo: step2 com `motorista_carona=True`  
- Portar: sim, 1:1

### 6.2 Custeio

4) Regra: custeio OUTRA_INSTITUICAO exige nome da instituicao  
- Onde: `Oficio.clean`, `OficioStep1Form.clean`, `oficio_step1`  
- Mensagem: "Informe a instituicao de custeio"  
- Portar: sim, 1:1

5) Regra: outros tipos de custeio limpam instituicao  
- Onde: `Oficio.clean/save`, `OficioStep1Form.clean`  
- Portar: sim

### 6.3 Motorista e carona

6) Regra: motorista pode ser servidor finalizado ou manual  
- Onde: `OficioStep2Form`  
- Disparo: selecao/autocomplete ou modo manual  
- Portar: sim

7) Regra: carona e inferida automaticamente  
- Onde: `OficioStep2Form._resolve_carona_preview` e `clean`  
- Criterio: motorista manual ou servidor fora do conjunto de viajantes do oficio  
- Portar: sim, 1:1

8) Regra: carona exige oficio/protocolo do motorista  
- Onde: `OficioStep2Form.clean`  
- Mensagens: numero e protocolo obrigatorios  
- Portar: sim, 1:1

9) Regra: referencia de carona para outro oficio  
- Onde: `oficio_step2`, `_autosave_oficio_step2`  
- Criterio: busca por numero/ano  
- Portar: sim, com cuidado de cardinalidade

### 6.4 Roteiro/trechos/retorno

10) Regra: Step 3 pode usar roteiro salvo ou proprio  
- Onde: `oficio_step3`, `_build_step3_route_options`, `_build_step3_state_from_*`  
- Portar: sim

11) Regra: validacao estrutural de state do Step 3  
- Onde: `_validate_step3_state`  
- Portar: sim, 1:1

12) Regra: persistencia de trechos no model `OficioTrecho`  
- Onde: `_salvar_step3_oficio`  
- Portar: sim

13) Regra: retorno separado dos trechos de ida  
- Onde: campos `retorno_*` em `Oficio`  
- Portar: sim

14) Regra: estimativa de rota e tempo adicional  
- Onde: `estimativa_local.py` + estado JS Step3  
- Portar: adaptar por provider/infra do novo projeto

### 6.5 Diarias

15) Regra: tipo destino por classificacao geografica (Interior/Capital/Brasilia)  
- Onde: `services/diarias.py` (`classify`, `infer_tipo_destino_from_paradas`)  
- Portar: sim

16) Regra: calculo periodizado (100%, 15%, 30%) com ajuste por pernoite  
- Onde: `build_periods`, `calculate_periodized_diarias`  
- Portar: sim, 1:1

17) Regra: valor por extenso com fallback manual  
- Onde: `valor_por_extenso_ptbr`  
- Portar: sim

### 6.6 Justificativa

18) Regra: justificativa exigida por antecedencia < prazo configurado  
- Onde: `services/justificativa.py` + `_build_oficio_justificativa_info` + `_validate_oficio_for_finalize`  
- Default prazo: 10 dias (configuravel)  
- Portar: sim, 1:1

19) Regra: disponibilidade condicionada ao schema de BD  
- Onde: `services/oficio_schema.py`  
- Mensagem: schema indisponivel bloqueia fluxo  
- Portar: adaptar no novo para migracao definitiva (ideal: sempre disponivel)

### 6.7 Finalizacao

20) Regra: finalizacao bloqueada com pendencias de step1/2/3/justificativa  
- Onde: `_validate_oficio_for_finalize`, `oficio_step4`  
- Portar: sim, 1:1

21) Regra: finalizacao seta status FINALIZADO sem congelar edicao futura por desenho atual  
- Onde: `oficio_step4`, `_save_oficio_preserving_status`  
- Portar: adaptar conforme politica do novo sistema

### 6.8 Exclusao

22) Regra: exclusao bloqueada se evento finalizado  
- Onde: `oficio_excluir`  
- Portar: sim

23) Regra: numero excluido volta a lacuna e pode ser reutilizado  
- Onde: `excluir_confirm.html` + algoritmo de lacuna na criacao  
- Portar: sim

### 6.9 Documentos

24) Regra: status de geracao por documento/formato (available/pending/unavailable/planned)  
- Onde: `validators.py`, `views.py`, `views_global.py`  
- Portar: sim

25) Regra: validacoes documentais especializadas por tipo (oficio/justificativa/termo/PT/OS)  
- Onde: `validate_oficio_for_document_generation` e auxiliares  
- Portar: sim

26) Regra: dependencia de backend DOCX/PDF e templates fisicos  
- Onde: `backends.py`, `renderer.py`  
- Portar: adaptar para stack do novo projeto

### 6.10 Autosave

27) Regra: autosave em POST XHR com flag `autosave=1` + `X-Requested-With`  
- Onde: `_is_autosave_request`, `_autosave_*`, `oficio_wizard.js`  
- Portar: sim

28) Regra: salvamento em `pagehide`/`visibilitychange` com `sendBeacon`  
- Onde: `oficio_wizard.js`  
- Portar: sim, se UX equivalente for desejada

---

## 7. Inventario de acoes do usuario

Acoes principais levantadas:
- Criar oficio avulso
- Criar oficio vinculado ao evento
- Editar oficio (sempre abre Step1)
- Excluir oficio
- Avancar/voltar no wizard
- Salvar em cada step
- Autosave silencioso
- Buscar e selecionar viajante
- Remover viajante selecionado
- Cadastrar novo viajante a partir do Step1/Step2
- Selecionar modelo de motivo
- Salvar motivo atual como novo modelo
- Alterar custeio e instituicao
- Buscar placa (autocomplete)
- Autopreencher dados de viatura por placa
- Cadastrar nova viatura a partir do Step2
- Buscar motorista (autocomplete)
- Alternar motorista servidor/manual
- Preencher dados de carona
- Selecionar modo de roteiro (salvo/proprio)
- Selecionar roteiro salvo
- Adicionar/remover destino
- Editar trechos de ida
- Estimar retorno automaticamente
- Ajustar tempos adicionais
- Calcular diarias
- Salvar roteiro para reutilizacao
- Abrir justificativa
- Aplicar modelo de justificativa
- Editar texto final da justificativa
- Marcar gerar termo preenchido
- Finalizar oficio
- Abrir central de documentos do oficio
- Baixar DOCX/PDF por tipo documental
- Filtrar lista global de oficios

Por acao, views/templates/js envolvidos:
- Wizard core: `oficio_step1/2/3/4`, templates `wizard_step*.html`, JS inline + `oficio_wizard.js`
- Justificativa: `oficio_justificativa`, template `justificativa.html`
- Documentos: `oficio_documentos`, `oficio_documento_download`, template `documentos.html`
- Exclusao: `oficio_excluir`, template `excluir_confirm.html`
- Global list/filter: `oficio_global_lista`, template `oficios_lista.html`

---

## 8. Dependencias com outros modulos

### 8.1 Cadastros

- `cadastros.Viajante`:
  - usado em viajantes do oficio, motorista servidor, assinaturas documentais
  - requisito forte: status FINALIZADO
- `cadastros.Veiculo` e combustivel:
  - lookup/autocomplete por placa
  - prefill de modelo/combustivel/tipo_viatura
- `cadastros.ConfiguracaoSistema`:
  - prazo de justificativa
  - dados institucionais para documentos
- `cadastros.AssinaturaConfiguracao`:
  - assinaturas por tipo de documento

### 8.2 Geografia

- `cadastros.Estado` / `cadastros.Cidade`:
  - sede, destinos, trechos, retorno
  - tipo destino e regras de diarias

### 8.3 Evento e fluxo guiado

- `Evento` e etapas guiadas:
  - hub de oficios no evento (Etapa 5)
  - sincronizacao de participantes
  - dados de fundamentacao para documentos PT/OS

### 8.4 Roteiros

- `RoteiroEvento`:
  - Step3 no modo EVENTO_EXISTENTE
  - mecanismo de reutilizacao de roteiros

### 8.5 Documentos

- modulo `eventos/services/documentos/*`:
  - context builder
  - validadores
  - renderer DOCX/PDF
  - metadados de tipos documentais

### 8.6 Dependencias tecnicas externas

- renderizacao DOCX/PDF conforme backend disponivel
- `num2words` para valor por extenso (fallback manual se indisponivel)

Risco de portar errado (alto):
- validacao de finalizacao e justificativa por antecedencia
- regras de carona do motorista
- composicao de Step3 e persistencia de trechos/retorno
- validadores documentais multi-tipo
- numeração por lacuna anual com concorrencia

---

## 9. Comportamentos de front-end

Comportamentos mapeados e arquivos:

1) Header sticky do wizard  
- `templates/eventos/oficio/_wizard_header.html`  
- `static/js/oficio_wizard.js` (`setStickyHeaderOffset`)  
- `static/css/style.css` (`.oficio-wizard-header`)

2) Stepper de etapas  
- `templates/eventos/oficio/_wizard_stepper.html`  
- classes `.oficio-stepper*`

3) Quick report lateral fixo  
- templates `wizard_step1/2/3`, `justificativa`  
- `oficio_wizard.js` (`syncQuickReportLayout`)  
- CSS `.oficio-quick-report.is-viewport-fixed`

4) Autosave em toda jornada  
- `oficio_wizard.js` (`createAutosave`)  
- hooks no submit, click em links, pagehide, visibilitychange

5) Autocomplete/chips/toggles  
- Step1: viajantes (chips)  
- Step2: motorista (chip unico)  
- Step2: toggle motorista manual  
- Step2: toggle exibicao campos carona

6) Mascaras de campo  
- `masks.js` (`data-mask`)  
- protocolo, placa, cpf, rg, telefone

7) Cards globais de oficios/documentos  
- `oficios_lista.html`  
- CSS `.oficio-process-*`, `.oficio-document-*`

8) Resumo final com grid e cards de escolha  
- `wizard_step4.html`  
- CSS `.oficio-summary-*`, `.oficio-choice-*`

9) Responsividade  
- media queries no `style.css` para stepper, quick report e cards

Itens a preservar no novo projeto:
- UX de wizard orientado por etapas
- quick report persistente
- autosave continuo
- autocomplete com chips
- feedback visual claro de pendencias de finalizacao

---

## 10. Pontos que dependem de eventos

Dependencia forte de evento:
- criacao via Etapa 5 (`guiado_etapa_3_criar_oficio`)
- sincronizacao de participantes do evento no Step1
- bloqueio de exclusao quando evento finalizado
- documento PT/OS condicionado a fundamentacao do evento
- rotas de retorno para painel/etapas

Dependencia fraca ou opcional:
- wizard de oficio avulso funciona sem evento
- documentos de oficio/justificativa/termo podem ser gerados para oficio sem evento conforme validacao

Reinterpretacao sem eventos (novo projeto):
- manter wizard autonomo de oficio
- encapsular integrações de evento em adaptadores (não no core do wizard)
- deixar sincronizacao de participantes como plugin de contexto

---

## 11. O que deve ser portado 1:1 para o projeto novo

- Estrutura funcional do wizard: Step1/2/3/4 + justificativa + documentos.
- Regras de validacao:
  - protocolo oficio
  - custeio e instituicao
  - carona motorista (numero/ano/protocolo)
  - finalizacao bloqueada por pendencias
  - justificativa por antecedencia/prazo
- Persistencia:
  - model de oficio com campos equivalentes
  - trechos separados em model proprio + retorno no oficio
- Numeracao anual por lacuna com unicidade `ano+numero`.
- Cálculo de diárias (periodizado, percentuais e valor por extenso).
- Status documental e validadores por tipo de documento.
- Autosave e quick report no front-end.

---

## 12. O que deve ser adaptado no projeto novo

- Camada de backend documental (DOCX/PDF) conforme stack da nova infra.
- Estrategia de checagem de schema de justificativa (`oficio_schema`) para eliminar comportamento transitório.
- Integração de roteamento/estimativa (`routing_provider`, `estimativa_local`) com contratos mais explicitos.
- Politica de edição de oficio finalizado (atualmente permitido em steps 1-3 por desenho).
- Acoplamento de oficios com etapas do evento, caso o novo fluxo seja desacoplado por micro-modulo.

---

## 13. O que deve ser descartado

- Helpers legados duplicados sem uso principal (`_legacy_oficio_step2`, `_legacy_oficio_step4`) se o novo projeto já nascer com fluxo unificado.
- Mensagens/labels transitórios de indisponibilidade de schema quando o schema definitivo estiver garantido.
- Qualquer fallback de documento "planned" que não faça parte da entrega final do novo modulo.

---

## 14. Checklist final de reconstrucao do modulo no projeto novo

1. Modelar `Oficio` e `OficioTrecho` com campos e constraints equivalentes.
2. Portar normalizadores de protocolo/placa e regras de custeio.
3. Portar Step1 com viajantes, modelos de motivo e sincronizacao opcional com evento.
4. Portar Step2 com lookup de viatura, motorista servidor/manual e regra de carona.
5. Portar Step3 com sede/destinos/trechos/retorno e calculadora de diarias.
6. Portar service de diarias exatamente com regras de pernoite e percentuais.
7. Portar service de justificativa por antecedencia + prazo configuravel.
8. Portar Step4 com validacao consolidada de finalizacao por secao.
9. Portar tela de justificativa com modelo + texto final.
10. Portar central de documentos com status por tipo e formato.
11. Portar validadores de documento e context builders por tipo.
12. Portar lista global de oficios com filtros e cards documentais.
13. Portar autosave e quick report no front-end.
14. Revisar pontos de acoplamento com evento e transformar em interfaces de integracao.
15. Criar suite de testes espelhando cenarios criticos (carona, finalizacao, diarias, justificativa, documentos).

---

## Anexo A - Dependencia tela x arquivo x componente

### Step 1
- View: `eventos/views.py::oficio_step1`
- Form: `eventos/forms.py::OficioStep1Form`
- Template: `templates/eventos/oficio/wizard_step1.html`
- APIs: `oficio_step1_viajantes_api`
- JS: inline + `static/js/oficio_wizard.js`
- CSS: `static/css/style.css` classes `.oficio-*`

### Step 2
- View: `eventos/views.py::oficio_step2`
- Form: `eventos/forms.py::OficioStep2Form`
- Template: `templates/eventos/oficio/wizard_step2.html`
- APIs: `oficio_step2_motoristas_api`, `oficio_step2_veiculos_busca_api`, `oficio_step2_veiculo_api`
- JS: inline + `static/js/oficio_wizard.js` + `static/js/masks.js`

### Step 3
- View: `eventos/views.py::oficio_step3`
- Template: `templates/eventos/oficio/wizard_step3.html`
- API: `oficio_step3_calcular_diarias`
- Services: `diarias.py`, `estimativa_local.py`

### Justificativa
- View: `eventos/views.py::oficio_justificativa`
- Form: `eventos/forms.py::OficioJustificativaForm`
- Template: `templates/eventos/oficio/justificativa.html`
- Services: `justificativa.py`, `oficio_schema.py`

### Step 4
- View: `eventos/views.py::oficio_step4`
- Template: `templates/eventos/oficio/wizard_step4.html`
- Validator principal: `_validate_oficio_for_finalize`

### Documentos
- View: `oficio_documentos`, `oficio_documento_download`
- Template: `templates/eventos/oficio/documentos.html`
- Services: `eventos/services/documentos/*`

---

## Anexo B - Decisao de porte por classes/funcoes

Portar obrigatoriamente:
- `Oficio`, `OficioTrecho`
- `OficioStep1Form`, `OficioStep2Form`, `OficioJustificativaForm`
- `oficio_step1/2/3/4`, `oficio_justificativa`, `_validate_oficio_for_finalize`
- `services/diarias.py` (core)
- `services/justificativa.py` (core)
- `services/documentos/validators.py` (core)
- `services/documentos/context.py` (core de exportacao)
- `static/js/oficio_wizard.js` (autosave + sticky)

Portar com adaptacao:
- `views_global.py` (cards globais e filtros)
- `renderer.py` / backends de DOCX-PDF
- `estimativa_local.py` e provider de rota

Descartar/aposentar no novo:
- fluxos legados redundantes marcados como `_legacy_*` apos consolidacao
- verificacao temporaria de schema quando migracao estiver estabilizada

---

## Anexo C - Campos por etapa para especificacao funcional

Step 1 (Dados e viajantes):
- Ofício (display), protocolo, data de criacao, modelo de motivo, motivo, custeio, instituicao de custeio, viajantes.

Step 2 (Transporte):
- Placa, modelo, combustivel, tipo viatura, porte/transporte de armas, motorista servidor/manual, campos de carona (oficio/protocolo motorista).

Step 3 (Roteiro e diarias):
- Modo do roteiro, roteiro salvo, sede UF/cidade, destinos, trechos ida, retorno, estimativa de rota, calculo de diarias, tipo destino.

Justificativa:
- Modelo de justificativa, texto final da justificativa.

Step 4 (Resumo/finalizacao):
- Consolidado de Steps 1-3, status da justificativa, opcao de termo preenchido, salvar, finalizar, links de download.
