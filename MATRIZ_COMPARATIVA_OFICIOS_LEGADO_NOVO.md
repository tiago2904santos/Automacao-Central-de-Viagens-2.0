# Matriz comparativa definitiva — Módulo de Ofícios (sistema novo vs legado)

**Data:** Março 2026  
**Escopo:** Módulo de ofícios — modelagem, campos, fluxos, regras, documentos, navegação.  
**Base:** Código real do sistema novo (eventos, cadastros, services); legado descrito em relatórios do projeto (código legado não está no repositório atual).

---

## Aviso sobre a base do legado

O **código do sistema legado** (referenciado como `legacy/viagens/` nos relatórios) **não está presente** no repositório analisado. A comparação do lado legado foi feita com base **exclusivamente** nos relatórios existentes:

- `RELATORIO_LEGADO_ETAPA3_COMPOSICAO.md`
- `RELATORIO_OFICIOS_REFATORACAO_LEGADO.md`
- `RELATORIO_ETAPA3_OFICIOS_LEGADO.md`
- `RELATORIO_OFICIOS_ATUAL.md`

Sempre que um detalhe do legado não puder ser confirmado por esses relatórios, está indicado: **«não foi possível confirmar no código»** (referindo-se à impossibilidade de inspecionar o código legado neste workspace).

---

## 1. MODELAGEM — Comparação entidade a entidade

| Entidade | Existe no novo? | Existe no legado? | Nome model novo | Nome model legado | Campos equivalentes | Campos ausentes no novo | Campos ausentes no legado | Semântica diferente | Aderência | Observações |
|----------|-----------------|-------------------|-----------------|-------------------|---------------------|--------------------------|---------------------------|---------------------|-----------|-------------|
| **Ofício** | Sim | Sim (relatórios) | `Oficio` | Oficio (não foi possível confirmar nome exato no código) | evento, viajantes, veiculo, motorista_viajante, motorista, motorista_carona, motorista_oficio*, motorista_protocolo, numero, ano, protocolo, motivo, custeio_tipo, nome_instituicao_custeio, tipo_destino, placa, modelo, combustivel, tipo_viatura, status, carona_oficio_referencia | Campo textual único "ofício" (N/AAAA) no legado pode existir como display; assunto/assunto_tipo não confirmados no novo | Não foi possível confirmar no código | Numeração: novo gera automaticamente por lacuna; legado pode ter fluxo distinto (não foi possível confirmar no código) | Forte | Novo tem roteiro_evento, roteiro_modo, estado_sede, cidade_sede, data_criacao, justificativa_texto, justificativa_modelo, modelo_motivo, retorno estruturado, diárias, porte_transporte_armas; ver seção 2. |
| **Trecho** | Sim | Não foi possível confirmar no código (relatórios falam em step 3 e trechos) | `OficioTrecho` | — | ordem, origem/destino (estado/cidade), saida/chegada data/hora, distancia_km, duracao | — | — | — | Parcial (legado não descrito como model separado nos relatórios) | Legado: _seed_trechos_from_evento_roteiros; novo: OficioTrecho com FK Estado/Cidade, estimativa local. |
| **Roteiro** | Sim (do evento) | Não foi possível confirmar no código | `RoteiroEvento` | — | evento, origem (sede), destinos, saida_dt, chegada_dt, retorno | — | — | No legado roteiro é do evento; step 3 ofício “seedado” do evento (não foi possível confirmar model próprio de roteiro do ofício no código) | Parcial | Novo: RoteiroEvento + RoteiroEventoDestino + RoteiroEventoTrecho; ofício usa roteiro_evento (FK) ou trechos próprios (OficioTrecho). |
| **OficioRoteiro** | Não como model | Não foi possível confirmar no código | — | — | — | — | — | — | N/A | Novo: vínculo por Oficio.roteiro_evento (FK RoteiroEvento) + OficioTrecho para roteiro próprio. |
| **PlanoTrabalho** | Não (documento gerado) | Não foi possível confirmar no código | — | — | — | — | — | — | N/A | Novo: geração por evento/services/documentos (plano_trabalho.py + context EventoFundamentacao); não há model PlanoTrabalho. |
| **OrdemServico** | Não (documento gerado) | Não foi possível confirmar no código | — | — | — | — | — | — | N/A | Idem: geração por ordem_servico.py + context. |
| **TermoAutorizacao** | Não (documento gerado) | Não foi possível confirmar no código | — | — | — | — | — | — | N/A | Novo: termo_autorizacao.py + template .docx; EventoTermoParticipante (evento) para status por participante. |
| **Evento** (parte que impacta ofício) | Sim | Sim | `Evento` | Evento | titulo, data_inicio, data_fim, status; vínculo oficios | veiculo, motorista no evento não são usados para pré-preencher ofício no novo | Não foi possível confirmar no código | — | Forte | Novo: evento.oficios; Etapa 3 = hub de ofícios; composição só no ofício. |
| **DocumentoEventoArquivo / equivalente** | Não | Não foi possível confirmar no código | — | — | — | — | — | — | N/A | Novo: geração sob demanda (DOCX/PDF) sem model de arquivo persistido. |
| **ModeloMotivoViagem** | Sim | Não foi possível confirmar nome no código | `ModeloMotivoViagem` | — | nome, texto (motivo), ativo, padrao | codigo, ordem no novo | — | — | Parcial (legado não detalhado) | Novo: codigo único, build_unique_codigo. |
| **ModeloJustificativa** | Sim | Não foi possível confirmar no código | `ModeloJustificativa` | — | nome, texto, padrao, ativo | — | — | — | Parcial | Novo: usado por justificativa_texto / modelo no ofício (justificativa_modelo FK). |
| **ConfiguracaoOficio / OficioConfig** | Não como model dedicado | Não foi possível confirmar no código | — | — | — | — | — | — | N/A | Novo: ConfiguracaoSistema (cadastros) com cidade_sede_padrao, prazo_justificativa_dias, assinaturas (AssinaturaConfiguracao por tipo). |

---

## 2. OFÍCIO — Comparação campo a campo

| Campo / regra | Equivalente no novo | Equivalente no legado | Aderência | Lacuna | Risco |
|---------------|---------------------|------------------------|-----------|--------|-------|
| numero | Oficio.numero (PositiveIntegerField, db_index) | numero (relatórios) | Forte | — | Baixo |
| ano | Oficio.ano (PositiveIntegerField, db_index) | ano (relatórios) | Forte | — | Baixo |
| Campo textual legado "ofício" (ex.: N/AAAA) | numero_formatado (property, ex.: 01/2026) | Não foi possível confirmar no código se existe campo único textual | Parcial | Legado pode ter campo único editável; novo só display | Baixo |
| protocolo | Oficio.protocolo (CharField 80); normalize_protocolo; 9 dígitos em clean/save | protocolo (relatórios); obrigatório step 1 | Forte | — | Baixo |
| status | Oficio.status (RASCUNHO, FINALIZADO) | status RASCUNHO/FINALIZADO (relatórios) | Forte | — | Baixo |
| assunto / assunto_tipo | Não existe no model | Não foi possível confirmar no código | — | Se legado tiver assunto/assunto_tipo, novo não tem | Médio |
| tipo_destino | Oficio.tipo_destino (INTERIOR, CAPITAL, BRASILIA) | tipo_destino (relatórios) | Forte | — | Baixo |
| estado/cidade sede | Oficio.estado_sede, Oficio.cidade_sede (FK) | Não explicitado nos relatórios para o ofício | Parcial | — | Baixo |
| estado/cidade destino | Implícito em OficioTrecho (destino_estado, destino_cidade) e roteiro | Destinos por trechos/roteiro (relatórios) | Forte | — | Baixo |
| retorno estruturado | retorno_saida_cidade/data/hora, retorno_chegada_cidade/data/hora | Não detalhado nos relatórios | Parcial | — | Baixo |
| quantidade_diarias | Oficio.quantidade_diarias (CharField 120) | Não foi possível confirmar no código | Parcial | — | Baixo |
| valor_diarias | Oficio.valor_diarias (CharField 80) | Não foi possível confirmar no código | Parcial | — | Baixo |
| valor_diarias_extenso | Oficio.valor_diarias_extenso (TextField) | Não foi possível confirmar no código | Parcial | — | Baixo |
| tipo_viatura | Oficio.tipo_viatura (CARACTERIZADA, DESCARACTERIZADA) | tipo_viatura (relatórios) | Forte | — | Baixo |
| custeio_tipo | Oficio.custeio_tipo (UNIDADE, OUTRA_INSTITUICAO, ONUS_LIMITADOS) | custeio (relatórios) | Forte | — | Baixo |
| nome_instituicao_custeio | Oficio.nome_instituicao_custeio; obrigatório se OUTRA_INSTITUICAO (clean/save) | nome_instituicao_custeio (relatórios) | Forte | — | Baixo |
| veiculo | Oficio.veiculo (FK cadastros.Veiculo) | veiculo FK (relatórios) | Forte | — | Baixo |
| placa | Oficio.placa (CharField 10) | placa (relatórios) | Forte | — | Baixo |
| modelo | Oficio.modelo (CharField 120) | modelo (relatórios) | Forte | — | Baixo |
| combustivel | Oficio.combustivel (CharField 80) | combustivel (relatórios) | Forte | — | Baixo |
| motorista | Oficio.motorista (CharField 120, nome) | motorista (relatórios) | Forte | — | Baixo |
| motorista_viajante | Oficio.motorista_viajante (FK Viajante) | motorista_viajante (relatórios) | Forte | — | Baixo |
| motorista_carona | Oficio.motorista_carona (BooleanField) | motorista_carona (relatórios) | Forte | — | Baixo |
| motorista_oficio_numero / motorista_oficio_ano | Oficio.motorista_oficio_numero, motorista_oficio_ano | motorista_oficio_numero, motorista_oficio_ano (relatórios) | Forte | — | Baixo |
| motorista_oficio | Oficio.motorista_oficio (CharField, ex.: N/AAAA) | motorista_oficio (relatórios) | Forte | — | Baixo |
| motorista_protocolo | Oficio.motorista_protocolo (CharField 80); normalização por máscara | motorista_protocolo (relatórios); obrigatório se carona | Forte | — | Baixo |
| carona_oficio_referencia | Oficio.carona_oficio_referencia (FK self); existe mas view ativa não preenche (RELATORIO_OFICIOS_ATUAL) | carona_oficio_referencia (relatórios) | Parcial | Uso explícito na UI/flow não confirmado no novo | Baixo |
| motivo | Oficio.motivo (TextField) | motivo (relatórios) | Forte | — | Baixo |
| modelo_motivo | Oficio.modelo_motivo (FK ModeloMotivoViagem) | Não foi possível confirmar no código | Parcial | — | Baixo |
| justificativa_modelo | Oficio.justificativa_modelo (FK ModeloJustificativa) | Não foi possível confirmar no código | Parcial | — | Baixo |
| justificativa_texto | Oficio.justificativa_texto (TextField) | Não foi possível confirmar no código | Parcial | — | Baixo |
| viajantes | Oficio.viajantes (M2M Viajante) | viajantes M2M (relatórios) | Forte | — | Baixo |
| created_at / updated_at | Oficio.created_at, updated_at | Não foi possível confirmar no código | Forte | — | Baixo |
| evento | Oficio.evento (FK Evento, null=True, blank=True) | evento FK (relatórios) | Forte | — | Baixo |
| data_criacao | Oficio.data_criacao (DateField); default timezone.localdate() em clean/save | Não foi possível confirmar no código | Parcial | — | Baixo |
| roteiro_evento | Oficio.roteiro_evento (FK RoteiroEvento); roteiro_modo (EVENTO_EXISTENTE / ROTEIRO_PROPRIO) | Step 3 seedado do evento (relatórios) | Forte | — | Baixo |
| porte_transporte_armas | Oficio.porte_transporte_armas (BooleanField, default True) | Não foi possível confirmar no código | Parcial | — | Baixo |

---

## 3. FLUXO FUNCIONAL

| Fluxo | Comportamento no legado | Comportamento no novo | Equivalência | Divergência | Impacto prático |
|-------|--------------------------|------------------------|--------------|-------------|------------------|
| **Wizard de criação** | oficios/novo → formulario; evento_id na sessão; steps 1–2 (dados + transporte), step 3 (trechos), step 4 (resumo) (relatórios) | guiado_etapa_3_criar_oficio → Oficio.objects.create(evento=evento) → redirect oficio-step1; steps 1–4 em oficio_step1/2/3/4 (eventos/views.py) | Forte | Novo numera automaticamente na criação; legado não detalhado (não foi possível confirmar no código) | Baixo |
| **Wizard de edição** | oficios/<id>/editar/etapa-1 etc.; _apply_step1_to_oficio, _apply_step2_to_oficio (relatórios) | oficio_editar redireciona para oficio-step1 (eventos/views.py); mesma lógica de steps | Forte | — | Baixo |
| **Tela única de edição** | Não foi possível confirmar no código | Não existe; edição é pelo wizard (step1) | N/A | — | — |
| **Lista global de ofícios** | Não foi possível confirmar no código (relatórios citam apenas Etapa 3 por evento) | Não existe; listagem só por evento em guiado_etapa_3 (evento.oficios.order_by('ano','numero','id')) | Parcial | Novo não tem lista global; pode ser requisito futuro | Médio |
| **Lista por evento** | evento_guiado_etapa3; evento.oficios; tabela número/ano, protocolo, destino (tipo_destino), status, Editar, Central de Documentos (relatórios) | guiado_etapa_3; evento.oficios.order_by('ano','numero','id'); tabela com número, protocolo, tipo_destino, status, Editar, Documentos, Excluir (templates/eventos/guiado/etapa_3.html) | Forte | Novo tem Excluir; Central de Documentos no novo = tela documentos (download DOCX/PDF) | Baixo |
| **Central de documentos** | Link "Central de Documentos" na lista do evento (relatórios); geração ofício, justificativa, plano, ordem, termos (relatórios) | oficio_documentos (eventos/views.py); tela com cards por tipo (Ofício, Justificativa, Termo, PT, OS) e download DOCX/PDF (templates/eventos/oficio/documentos.html) | Forte | Implementação real no novo (services/documentos); legado não foi possível confirmar no código | Baixo |
| **Exclusão** | Não foi possível confirmar no código | oficio_excluir (eventos/views.py); bloqueada se evento finalizado; confirmação (excluir_confirm.html) | Parcial | Comportamento de bloqueio por evento finalizado é do novo | Baixo |
| **Rascunho / finalização** | Status RASCUNHO/FINALIZADO; Step 4 finalizar (relatórios) | oficio_step4 POST "finalizar" → status = FINALIZADO; validação _validate_oficio_for_finalize (justificativa obrigatória quando antecedência < prazo) | Forte | Novo tem validação explícita de justificativa por prazo (eventos/services/justificativa.py) | Baixo |
| **Redirecionamentos a partir do evento** | Etapa 3 → Criar ofício → wizard; Editar → etapa-1; Central de Documentos (relatórios) | Etapa 3 → criar → oficio-step1; Editar → oficio-step1; Documentos → oficio-documentos; Step 4 "Voltar para Ofícios do evento" → guiado-etapa-3 | Forte | — | Baixo |

---

## 4. REGRAS DE NEGÓCIO

| Regra | Onde está no legado | Onde está no novo | Reproduzida? | Parcial? | Não reproduzida? | Diferença aceitável / problema |
|-------|----------------------|--------------------|--------------|----------|------------------|---------------------------------|
| Numeração única por ano | Não foi possível confirmar no código | Oficio.save(): get_next_available_numero(ano); UniqueConstraint(ano, numero); retry IntegrityError (eventos/models.py) | Sim | — | — | Aceitável |
| Sincronização número/ano e campo textual | Não foi possível confirmar no código | numero_formatado (property); não há campo textual editável separado | — | Sim | — | Lacuna se legado tiver campo textual único N/AAAA editável |
| Protocolo 9 dígitos | Relatórios citam protocolo obrigatório | Oficio.clean/save: normalize_protocolo; ValidationError se len != 9 (eventos/models.py); core/utils/masks | Sim | — | — | Aceitável |
| Protocolo motorista 9 dígitos | Não foi possível confirmar no código | motorista_protocolo armazenado; form Step 2 valida quando carona; máscara em masks.js | Parcial | — | — | Validação estrita de 9 dígitos no model não confirmada para motorista_protocolo |
| Motorista carona exige ofício + ano + protocolo | _validate_edit_wizard_data; step 2 (relatórios) | OficioStep2Form: se motorista_carona, motorista_oficio_numero, motorista_oficio_ano, motorista_protocolo obrigatórios (eventos/forms.py); view step2 | Sim | — | — | Aceitável |
| Custeio outra instituição exige nome | Não foi possível confirmar no código | Oficio.clean/save: se CUSTEIO_OUTRA_INSTITUICAO exige nome_instituicao_custeio (eventos/models.py) | Sim | — | — | Aceitável |
| Conversão/normalização tipos custeio | Não foi possível confirmar no código | Choices iguais aos dos relatórios; sem conversão de valores legados | — | — | — | N/A |
| Justificativa obrigatória se antecedência < 10 dias | Relatórios citam justificativa por prazo | oficio_exige_justificativa (eventos/services/justificativa.py); get_prazo_justificativa_dias() de ConfiguracaoSistema (default 10); _validate_oficio_for_finalize bloqueia finalização (eventos/views.py) | Sim | — | — | Aceitável |
| Destino institucional automático (GAB/SESP) | Não foi possível confirmar no código | Não implementado | — | — | Sim | Lacuna se legado tiver |
| Tipo destino geográfico derivado dos trechos | Não foi possível confirmar no código | eventos/services/diarias.py inferência tipo_destino; Step 3 preenche tipo_destino no ofício | Parcial | — | — | Aceitável |
| Cálculo de diárias | Não foi possível confirmar no código | eventos/services/diarias.py; oficio_step3_calcular_diarias (views); quantidade_diarias, valor_diarias, valor_diarias_extenso | Parcial | — | — | Aceitável |
| Pré-condições para finalização | _validate_edit_wizard_data (relatórios) | _validate_oficio_for_finalize: steps 1–3, trechos, retorno, justificativa se exigida (eventos/views.py) | Sim | — | — | Aceitável |
| Relação ofício ↔ plano de trabalho | Não foi possível confirmar no código | PT gerado por plano_trabalho.py; contexto usa evento.fundamentacao.texto_fundamentacao se tipo PT (context.py) | Parcial | — | — | Aceitável |
| Relação ofício ↔ ordem de serviço | Não foi possível confirmar no código | OS gerada por ordem_servico.py; contexto usa evento.fundamentacao se tipo OS | Parcial | — | — | Aceitável |
| Relação ofício ↔ termo de autorização | Termos por (ofício, viajante) (relatórios) | termo_autorizacao.py + template; EventoTermoParticipante no evento para status | Forte | — | — | Aceitável |
| Relação ofício ↔ evento | evento FK; etapa 3 hub (relatórios) | Oficio.evento; guiado_etapa_3; criação por guiado_etapa_3_criar_oficio | Sim | — | — | Aceitável |
| Documentos assinados / pacote do evento | Não foi possível confirmar no código | AssinaturaConfiguracao por tipo; geração sob demanda; não há “pacote” persistido | — | Sim | — | Divergência aceitável se legado tiver pacote físico |

---

## 5. DOCUMENTOS

| Documento | Onde é gerado no legado | Onde é gerado no novo | Template legado | Template novo | Placeholders/campos principais | Regras condicionais | DOCX | PDF | Aderência conteúdo | Aderência layout | Lacunas |
|-----------|--------------------------|------------------------|-----------------|---------------|--------------------------------|---------------------|------|-----|--------------------|------------------|---------|
| **Ofício** | Não foi possível confirmar no código | eventos/services/documentos/oficio.py; render_oficio_docx; build_oficio_template_context | Não foi possível confirmar no código | eventos/resources/documentos/oficio_model.docx | oficio, data_do_oficio, protocolo, nome_chefia, cargo_chefia, unidade, placa, viatura, combustivel, motorista_formatado, custo, diarias_x, diaria, valor_extenso, destinos_bloco, col_servidor, col_rgcpf, col_cargo, col_ida_saida/chegada, col_volta_*, col_solicitacao, motivo, telefone, etc. | Validação validate_oficio_for_document_generation | Sim | Sim (backend Windows) | Alta | Alta (após auditoria documental) | — |
| **Justificativa** | Não foi possível confirmar no código | eventos/services/documentos/justificativa.py; modelo_justificativa.docx | Não foi possível confirmar no código | modelo_justificativa.docx | sede, data_extenso, justificativa, assinante_justificativa, cargo_*, divisao, unidade, endereco, email, telefone | justificativa_texto obrigatório; validação no validator | Sim | Sim | Alta | Alta | — |
| **Termo de autorização** | Não foi possível confirmar no código | eventos/services/documentos/termo_autorizacao.py; termo_autorizacao_ascom.docx + post_processor | Não foi possível confirmar no código | termo_autorizacao_ascom.docx | data_do_evento, destino, divisao, email, endereco, telefone, unidade_rodape; pós-processo: parágrafos “Eu manifesto…”, Viatura, Placa/Combustível, Autorização Chefia | Destinos, período, viajantes; validators | Sim | Sim | Alta | Alta | — |
| **Plano de trabalho** | Não foi possível confirmar no código | eventos/services/documentos/plano_trabalho.py; create_base_document (código); contexto com evento.fundamentacao se tipo PT | Não foi possível confirmar no código | Nenhum .docx; gerado por código | objetivo, local_periodo, participantes, roteiro_resumo, transporte, diárias, custeio, assinaturas | Objetivo = texto_fundamentacao (evento) se tipo PT, senão motivo | Sim | Sim | Alta | Média (estrutura fixa em código) | Modelo .docx oficial de PT não existe no repo |
| **Ordem de serviço** | Não foi possível confirmar no código | eventos/services/documentos/ordem_servico.py; modelo_ordem_servico.docx | Não foi possível confirmar no código | modelo_ordem_servico.docx | cargo_chefia, data_extenso, destino, divisao, equipe_deslocamento, motivo, nome_chefia, ordem_de_servico, sede, unidade, email, endereco, telefone | Finalidade = texto_fundamentacao (evento) se tipo OS, senão motivo | Sim | Sim | Alta | Alta | — |

---

## 6. NAVEGAÇÃO E UX DO MÓDULO

| Item | Legado | Novo | Equivalência | Observação |
|------|--------|------|--------------|------------|
| Entrada no menu | Não foi possível confirmar no código | Menu lateral (core/navigation.py); item Ofícios pode levar a "Em breve" ou lista; acesso real via Eventos → evento → Fluxo guiado → Etapa 3 | Parcial | Lista global de ofícios não existe no novo |
| Lista global | Não foi possível confirmar no código | Inexistente; só lista por evento (guiado_etapa_3) | Parcial | Lacuna se legado tiver lista global |
| Central de documentos | Link por ofício na Etapa 3 (relatórios) | oficio-documentos (tela com cards DOCX/PDF por tipo) | Forte | Funcional no novo |
| Acesso via evento | Etapa 3 → lista de ofícios do evento (relatórios) | guiado_etapa_3 → evento.oficios; criar, editar, documentos, excluir | Forte | — |
| Status visual do ofício | Rascunho / Finalizado (relatórios) | Badge na lista (etapa_3.html); RASCUNHO / FINALIZADO | Forte | — |
| Continuidade de rascunho | Não foi possível confirmar no código | Wizard steps 1–4; salvar em cada step; editar reabre step 1 | Forte | — |
| Experiência de edição | Editar → etapa-1 (relatórios) | Editar → oficio-step1 (wizard) | Forte | — |

---

## 7. CLASSIFICAÇÃO FINAL

### A) JÁ EQUIVALENTE

- Modelo Oficio (campos principais: evento, viajantes, veiculo, motorista*, numero, ano, protocolo, motivo, custeio_tipo, nome_instituicao_custeio, tipo_destino, placa, modelo, combustivel, tipo_viatura, status, retorno, diárias).
- OficioTrecho (trechos de ida); retorno no próprio Oficio.
- Etapa 3 do evento = hub de ofícios; lista por evento; criar ofício no contexto do evento.
- Wizard steps 1–4: Step 1 (dados + viajantes), Step 2 (transporte + motorista/carona), Step 3 (sede, destinos, trechos, retorno, diárias), Step 4 (resumo + finalizar).
- Regras: protocolo 9 dígitos; numeração única por ano (lacuna); custeio OUTRA_INSTITUICAO exige nome; motorista carona exige ofício número/ano e protocolo; justificativa obrigatória por prazo (antecedência < 10 dias); pré-condições para finalização.
- Geração de documentos: Ofício, Justificativa, Termo, PT, OS (DOCX/PDF quando ambiente permite).
- Exclusão de ofício (com bloqueio se evento finalizado).
- Navegação: acesso via evento → Etapa 3 → lista, editar, documentos.

### B) PARCIAL

- carona_oficio_referencia: existe no model; não é preenchido pela view ativa (RELATORIO_OFICIOS_ATUAL).
- Lista global de ofícios: não existe no novo; legado não confirmado no código.
- Assunto/assunto_tipo: não existem no novo; legado não confirmado no código.
- Tipo destino derivado dos trechos: implementado em diarias.py; aderência total ao legado não confirmada.
- Cálculo de diárias: implementado; regras exatas do legado não foram possível confirmar no código.
- Plano de trabalho: gerado por código (sem .docx oficial no repo); conteúdo alinhado a EventoFundamentacao.
- Termo: EventoTermoParticipante no evento; termo gerado por ofício; relação evento↔termo parcialmente distinta do legado (não foi possível confirmar no código).

### C) NÃO IMPLEMENTADO NO NOVO

- Lista global de ofícios (se for requisito).
- Campo textual único “ofício” (N/AAAA) editável, se existir no legado (não foi possível confirmar no código).
- Assunto/assunto_tipo do ofício, se existirem no legado (não foi possível confirmar no código).
- Destino institucional automático (GAB/SESP), se existir no legado (não foi possível confirmar no código).
- Pacote de documentos do evento (arquivos persistidos), se existir no legado (não foi possível confirmar no código).

### D) NÃO DEVE SER COPIADO DO LEGADO

- Central de documentos “igual ao legado” como única forma de acesso: no novo a tela de documentos já é funcional (download por tipo).
- Duplicar composição no evento e no ofício: no legado composição é só no ofício; novo manteve isso (evento sem pré-preenchimento obrigatório de veículo/motorista para o ofício).
- Fluxo de numeração manual se o legado tiver: o novo adotou numeração automática por lacuna, mais robusta.
- Placeholders de edição/central antigos: já substituídos por wizard e tela de documentos reais.

---

## 8. MATRIZ FINAL (tabela resumo)

| Área | Item | Legado | Novo | Arquivos legado | Arquivos novo | Aderência | Lacuna | Risco | Prioridade | Ação recomendada |
|------|------|--------|------|-----------------|---------------|-----------|--------|-------|------------|-------------------|
| Modelagem | Oficio | Oficio (relatórios) | Oficio | Não disponível | eventos/models.py | Forte | assunto/assunto_tipo | Baixo | Média | Confirmar no legado se existe assunto; se sim, avaliar inclusão |
| Modelagem | Trecho | Step 3 / seed (relatórios) | OficioTrecho | Não disponível | eventos/models.py | Parcial | — | Baixo | Baixa | — |
| Modelagem | Roteiro | Evento (relatórios) | RoteiroEvento, RoteiroEventoTrecho | Não disponível | eventos/models.py | Parcial | — | Baixo | Baixa | — |
| Campo | protocolo 9 dígitos | Obrigatório (relatórios) | clean/save + normalize | Não disponível | eventos/models.py, core/utils/masks.py | Forte | — | Baixo | — | — |
| Campo | carona_oficio_referencia | FK (relatórios) | FK presente; não preenchido na view | Não disponível | eventos/models.py, views.py | Parcial | Uso na UI | Baixo | Baixa | Preencher em step2 quando carona se desejado |
| Fluxo | Lista global ofícios | Não confirmado | Inexistente | — | — | Parcial | Lista global | Médio | Alta | Implementar se requisito |
| Fluxo | Wizard criação/edição | Steps 1–4 (relatórios) | oficio_step1–4, oficio_editar→step1 | Não disponível | eventos/views.py, forms.py | Forte | — | Baixo | — | — |
| Fluxo | Central documentos | Link (relatórios) | oficio_documentos, download por tipo | Não disponível | eventos/views.py, services/documentos/ | Forte | — | Baixo | — | — |
| Regra | Justificativa < 10 dias | Citada (relatórios) | oficio_exige_justificativa; _validate_oficio_for_finalize | Não disponível | eventos/services/justificativa.py, views.py | Forte | — | Baixo | — | — |
| Regra | Numeração única/ano | Não confirmada | get_next_available_numero; UniqueConstraint | Não disponível | eventos/models.py | Forte | — | Baixo | — | — |
| Documentos | Ofício DOCX/PDF | Não confirmado | oficio.py, renderer, backends | Não disponível | eventos/services/documentos/ | Forte | — | Baixo | — | — |
| Documentos | PT/OS conteúdo evento | Não confirmado | context.py _get_fundamentacao_texto_para_tipo | Não disponível | eventos/services/documentos/context.py | Forte | — | Baixo | — | — |
| Navegação | Acesso por evento | Etapa 3 (relatórios) | guiado_etapa_3 | Não disponível | eventos/views.py, urls.py, guiado/etapa_3.html | Forte | — | Baixo | — | — |

---

## 9. SAÍDA FINAL OBRIGATÓRIA

### A) TOP 20 LACUNAS DO MÓDULO DE OFÍCIOS

1. Lista global de ofícios (inexistente no novo; não confirmada no código legado).  
2. Campo assunto/assunto_tipo do ofício (inexistente no novo; não confirmado no código legado).  
3. carona_oficio_referencia não preenchido na view ativa (model existe).  
4. Validação estrita de 9 dígitos para motorista_protocolo no model (máscara no form; clean do Oficio não valida motorista_protocolo).  
5. Destino institucional automático (GAB/SESP) não implementado (não confirmado no código legado).  
6. Pacote de documentos do evento (arquivos persistidos) não implementado (não confirmado no código legado).  
7. Modelo .docx oficial para Plano de Trabalho (novo gera por código).  
8. Campo textual único “ofício” (N/AAAA) editável, se existir no legado.  
9. Pré-preenchimento de veículo/motorista do evento para o ofício (novo não usa evento.veiculo/motorista).  
10. Ordenação explícita na listagem (novo usa ano, numero, id; legado não confirmado).  
11. Exibição de “Destino” na lista (novo exibe tipo_destino; destino geográfico completo não confirmado no legado).  
12. Integração Step 3 com roteiros do evento: modo EVENTO_EXISTENTE existe; equivalência total ao _seed_trechos_from_evento_roteiros não confirmada.  
13. TERMO_AUTORIZACAO em AssinaturaConfiguracao (cadastros): tipo existe; uso na geração do termo confirmado no novo.  
14. Justificativa por modelo (justificativa_modelo FK): existe no model; fluxo de seleção de modelo não detalhado nos relatórios.  
15. data_criacao: default no save/clean; não confirmado se legado tem campo equivalente.  
16. porte_transporte_armas: existe no novo; não confirmado no código legado.  
17. Exclusão de ofício: bloqueio quando evento finalizado; comportamento de reaproveitamento de lacuna na numeração (mencionado em excluir_confirm).  
18. APIs de viajantes/motoristas/veículos (step1/step2): novo tem; legado não detalhado.  
19. Máscaras (protocolo, placa, etc.): novo em masks.js e core/utils/masks.py; legado não confirmado.  
20. Configuração prazo_justificativa_dias: novo em ConfiguracaoSistema; legado não confirmado.

### B) TOP 10 REGRAS CRÍTICAS DO LEGADO AINDA NÃO REPRODUZIDAS (ou não confirmadas)

1. **Lista global de ofícios** — não existe no novo; não foi possível confirmar no código se o legado tem.  
2. **Assunto/assunto_tipo** — não existem no novo; não foi possível confirmar no código no legado.  
3. **Preenchimento de carona_oficio_referencia** — regra de preencher FK ao outro ofício quando carona; não aplicada na view ativa.  
4. **Destino institucional automático (GAB/SESP)** — não implementado; não foi possível confirmar no código no legado.  
5. **Validação 9 dígitos motorista_protocolo no model** — novo valida no form; clean() do Oficio não valida motorista_protocolo.  
6. **Pacote de documentos do evento** — não implementado; não foi possível confirmar no código no legado.  
7. **Campo “ofício” textual único (N/AAAA)** — não existe como campo editável no novo; não foi possível confirmar no código no legado.  
8. **Conversão/normalização de tipos de custeio** para migração de dados legados — não aplicável se não houver migração.  
9. **Ordenação e filtros da lista de ofícios** (por evento) — novo ordena por ano, numero, id; filtros por status não confirmados no legado.  
10. **Regra de “documentos assinados”** (workflow de assinatura) — novo usa AssinaturaConfiguracao para texto nos documentos; workflow de assinatura digital não foi possível confirmar no código no legado.

### C) TOP 10 DIVERGÊNCIAS ACEITÁVEIS

1. **Numeração automática por lacuna** no novo (legado pode ter numeração manual; não foi possível confirmar no código).  
2. **Sem lista global de ofícios** no novo (acesso só por evento); pode ser decisão de produto.  
3. **Central de documentos** no novo é tela de download por tipo (DOCX/PDF); legado pode ter fluxo diferente (não confirmado).  
4. **PT/OS** no novo usam EventoFundamentacao.texto_fundamentacao quando tipo PT/OS; legado não detalhado.  
5. **Exclusão com bloqueio** quando evento finalizado (reforço de integridade no novo).  
6. **Roteiro do ofício**: novo tem roteiro_evento (FK) + OficioTrecho; legado “seed” a partir do evento (não confirmado model).  
7. **Justificativa**: novo usa ConfiguracaoSistema.prazo_justificativa_dias (10) e oficio_exige_justificativa; regra alinhada aos relatórios.  
8. **Edição** sempre via step 1 no novo (oficio_editar → step1); legado editar etapa-1 (equivalente).  
9. **Sem pré-preenchimento** de veículo/motorista do evento no ofício; composição só no ofício (igual aos relatórios).  
10. **Geração de documentos** sob demanda (sem persistir arquivos); legado não foi possível confirmar no código.

### D) TOP 10 COISAS DO LEGADO QUE NÃO DEVEM SER COPIADAS CEGAMENTE

1. **Central de documentos** “igual ao legado” sem verificar se o novo (tela documentos + download por tipo) já atende.  
2. **Composição no evento** (viajantes, veículo, motorista no nível evento): relatórios dizem que no legado composição é só no ofício; não duplicar no evento.  
3. **Numeração manual** do ofício se o legado tiver: o novo com lacuna automática é mais seguro.  
4. **Placeholders** de edição/central antigos: já substituídos por wizard e documentos reais.  
5. **Campo textual único “ofício”** (N/AAAA) editável, se for apenas redundante com numero+ano.  
6. **Assunto/assunto_tipo** sem confirmação no código legado: não adicionar sem requisito claro.  
7. **Pacote de documentos persistido** sem requisito explícito (novo gera sob demanda).  
8. **Validações frouxas** de protocolo/motorista_protocolo: novo já exige 9 dígitos para protocolo.  
9. **Duplicar trechos** em dois models (roteiro evento vs ofício): novo já separa RoteiroEvento e OficioTrecho de forma coerente.  
10. **Workflow de assinatura** complexo sem confirmação no código legado: manter AssinaturaConfiguracao por tipo como está.

### E) PRÓXIMA ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

1. **Confirmar no código legado** (se disponível): lista global de ofícios; assunto/assunto_tipo; destino institucional GAB/SESP; pacote de documentos; campo “ofício” textual; validação motorista_protocolo 9 dígitos.  
2. **Implementar lista global de ofícios** se for requisito (view + template + URL; filtros opcionais por status/evento/ano).  
3. **Preencher carona_oficio_referencia** no Step 2 quando motorista carona e houver outro ofício selecionado (se desejado).  
4. **Incluir validação de 9 dígitos para motorista_protocolo** no Oficio.clean() quando motorista_carona e motorista_protocolo preenchido.  
5. **Adicionar assunto/assunto_tipo** ao Oficio somente se confirmado no legado ou exigido por produto.  
6. **Manter** numeração automática, regra de justificativa por prazo, bloqueio de exclusão quando evento finalizado, e geração de documentos atual.  
7. **Documentar** decisão de não ter lista global (se for o caso) e de não persistir pacote de documentos.  
8. **Auditoria visual** dos 5 documentos gerados em ambiente real (já recomendada em RELATORIO_AUDITORIA_DOCUMENTAL.md).

---

**Fim da matriz comparativa.**  
Para qualquer item marcado «não foi possível confirmar no código» (legado), a confirmação exige acesso ao repositório ou código-fonte do sistema legado.
