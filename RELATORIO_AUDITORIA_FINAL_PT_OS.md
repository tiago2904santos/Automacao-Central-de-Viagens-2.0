# 1. Resumo executivo
- Conclusão objetiva: o desacoplamento estrutural de PT/OS foi implementado no núcleo operacional (models, CRUD, rotas, fluxo guiado e geração documental), porém ainda existem resíduos legados de EventoFundamentacao no código (model, form, admin, testes e um helper não utilizado).
- PT/OS agora são realmente independentes ou não: são independentes no fluxo principal de operação (criação/edição/listagem/download sem obrigatoriedade de Evento ou Ofício), mas o legado não foi totalmente removido. Portanto, independência funcional: SIM; limpeza completa do legado: NÃO.

# 2. Base analisada
- Branch atual: refactor/arquitetura-documentos-independentes
- Commit HEAD: 7d0cc63
- Commit analisado: 7d0cc63
- Arquivos inspecionados:
  - eventos/models.py
  - eventos/forms.py
  - eventos/urls.py
  - eventos/views.py
  - eventos/views_global.py
  - eventos/services/documentos/context.py
  - eventos/services/documentos/plano_trabalho.py
  - eventos/services/documentos/ordem_servico.py
  - eventos/migrations/0031_ordemservico_documentoavulso_ordem_servico_and_more.py
  - eventos/admin.py
  - templates/eventos/guiado/etapa_4.html
  - templates/eventos/documentos/planos_trabalho_form.html
  - templates/eventos/documentos/ordens_servico_form.html
  - templates/eventos/global/documentos_hub.html
  - templates/eventos/global/documento_derivado_lista.html
  - eventos/tests/test_eventos.py
  - eventos/tests/test_global_views.py
  - eventos/tests/test_plano_trabalho.py

# 3. Models finais
Definições encontradas em eventos/models.py:
- PlanoTrabalho: classe própria (class PlanoTrabalho), com status RASCUNHO/FINALIZADO, campos de conteúdo PT e relacionamentos opcionais.
- OrdemServico: classe própria (class OrdemServico), com status RASCUNHO/FINALIZADO, campos de conteúdo OS e relacionamentos opcionais.
- EfetivoPlanoTrabalhoDocumento: classe própria para composição de efetivo vinculada ao PlanoTrabalho, com constraint única (plano_trabalho, cargo).

Campos de vínculo:
- PlanoTrabalho.evento: ForeignKey(Evento, SET_NULL, null=True, blank=True).
- PlanoTrabalho.oficio: ForeignKey(Oficio, SET_NULL, null=True, blank=True).
- OrdemServico.evento: ForeignKey(Evento, SET_NULL, null=True, blank=True).
- OrdemServico.oficio: ForeignKey(Oficio, SET_NULL, null=True, blank=True).

Status:
- PlanoTrabalho.STATUS_CHOICES: RASCUNHO, FINALIZADO.
- OrdemServico.STATUS_CHOICES: RASCUNHO, FINALIZADO.

Relacionamentos auxiliares:
- PlanoTrabalho.solicitante -> SolicitantePlanoTrabalho (opcional).
- PlanoTrabalho.coordenador_operacional -> CoordenadorOperacional (opcional).
- PlanoTrabalho.coordenador_administrativo -> cadastros.Viajante (opcional).
- EfetivoPlanoTrabalhoDocumento.plano_trabalho -> PlanoTrabalho (CASCADE).
- EfetivoPlanoTrabalhoDocumento.cargo -> cadastros.Cargo (PROTECT).

Conclusões explícitas:
- evento é opcional: SIM.
- oficio é opcional: SIM.
- PT e OS existem sem qualquer vínculo obrigatório: SIM.

# 4. Estado de EventoFundamentacao
Respostas objetivas:
- O model ainda existe? SIM (eventos/models.py, class EventoFundamentacao).
- Ainda está importado em views/forms/services?
  - forms: SIM (eventos/forms.py, import e class EventoFundamentacaoForm).
  - views: não há uso ativo no fluxo guiado PT/OS atual em eventos/views.py.
  - views_global: existe referência residual em helper _document_status_summary (usa evento.fundamentacao), mas sem chamada no código.
  - services/documentos: NÃO há leitura ativa de EventoFundamentacao em context.py/plano_trabalho.py/ordem_servico.py.
- Ainda participa de rotas? NÃO há rota dedicada a EventoFundamentacao em eventos/urls.py.
- Ainda participa de renderização de documentos? NÃO no fluxo atual de PT/OS.
- Ainda participa do fluxo guiado? NÃO no núcleo da etapa 4 atual (usa PlanoTrabalho/OrdemServico).
- Ainda participa de queries ativas? Apenas em resíduos:
  - helper não utilizado em views_global.py (_document_status_summary).
  - migração histórica/data migration (0031).
  - testes legados.
- Ainda participa de templates? Residual em templates/eventos/global/documento_derivado_lista.html via campo fundamentacao_label.

Referências restantes (classificação):

Uso ativo (núcleo operacional atual):
- Nenhum uso ativo identificado em rotas PT/OS, views de CRUD PT/OS, guiado etapa 4 e services documentais de PT/OS.

Compatibilidade temporária:
- eventos/migrations/0031_ordemservico_documentoavulso_ordem_servico_and_more.py
  - função migrate_fundamentacao_to_pt_os usa apps.get_model('eventos', 'EventoFundamentacao') para migração de legado.

Código morto/residual:
- eventos/models.py: class EventoFundamentacao permanece definida.
- eventos/forms.py: class EventoFundamentacaoForm permanece definida/importada.
- eventos/admin.py: EventoFundamentacaoAdmin permanece registrado.
- eventos/views_global.py: _document_status_summary referencia evento.fundamentacao; busca de uso mostra função sem chamadas.
- templates/eventos/global/documento_derivado_lista.html: usa row.status.fundamentacao_label.
- eventos/tests/test_eventos.py, eventos/tests/test_global_views.py, eventos/tests/test_plano_trabalho.py: múltiplas referências a EventoFundamentacao.

# 5. Rotas finais de PT/OS
Rotas reais criadas em eventos/urls.py:

Plano de Trabalho:
- lista: /eventos/documentos/planos-trabalho/
- novo: /eventos/documentos/planos-trabalho/novo/
- detalhe: /eventos/documentos/planos-trabalho/<pk>/
- editar: /eventos/documentos/planos-trabalho/<pk>/editar/
- excluir: /eventos/documentos/planos-trabalho/<pk>/excluir/
- download: /eventos/documentos/planos-trabalho/<pk>/download/<formato>/

Ordem de Serviço:
- lista: /eventos/documentos/ordens-servico/
- novo: /eventos/documentos/ordens-servico/novo/
- detalhe: /eventos/documentos/ordens-servico/<pk>/
- editar: /eventos/documentos/ordens-servico/<pk>/editar/
- excluir: /eventos/documentos/ordens-servico/<pk>/excluir/
- download: /eventos/documentos/ordens-servico/<pk>/download/<formato>/

# 6. Views finais de PT/OS
Views em eventos/views_global.py:
- planos_trabalho_global: lista paginada e filtros por q/evento/oficio/status.
- plano_trabalho_novo: criação real de PT.
- plano_trabalho_editar: edição real de PT.
- plano_trabalho_detalhe: detalhe real de PT.
- plano_trabalho_excluir: exclusão real de PT.
- plano_trabalho_download: geração de arquivo PT (com ofício ou sem ofício).
- ordens_servico_global: lista paginada e filtros por q/evento/oficio/status.
- ordem_servico_novo: criação real de OS.
- ordem_servico_editar: edição real de OS.
- ordem_servico_detalhe: detalhe real de OS.
- ordem_servico_excluir: exclusão real de OS.
- ordem_servico_download: geração de arquivo OS (com ofício ou sem ofício).

Conclusões explícitas:
- Funcionam sem evento: SIM (model/form aceitam null e view não exige evento).
- Funcionam sem ofício: SIM (model/form aceitam null e download tem fallback para render por model).
- Aceitam preselected_event_id: SIM (_resolve_preselected_context + initial).
- Aceitam preselected_oficio_id: SIM (_resolve_preselected_context + initial).
- Aceitam return_to: SIM (_get_safe_return_to em novo/editar/excluir).

# 7. Forms finais de PT/OS
Forms criados/alterados em eventos/forms.py:
- PlanoTrabalhoForm
  - campos: numero, ano, data_criacao, status, evento, oficio, solicitante, solicitante_outros, coordenador_operacional, coordenador_administrativo, coordenador_municipal, objetivo, locais, horario_atendimento, quantidade_servidores, metas_formatadas, efetivo_resumo, recursos_texto, observacoes, atividades_codigos.
  - evento opcional: SIM (required=False no __init__).
  - oficio opcional: SIM (required=False no __init__).
- OrdemServicoForm
  - campos: numero, ano, data_criacao, status, evento, oficio, finalidade, responsaveis, designacoes, determinacoes, observacoes.
  - evento opcional: SIM (required=False no __init__).
  - oficio opcional: SIM (required=False no __init__).
- DocumentoAvulsoForm (alterado)
  - incluiu ordem_servico e ajustou plano_trabalho para novo model.

Validação escondida obrigando contexto:
- Não identificada para forçar evento/ofício em PT/OS.
- As views aceitam contexto opcional (preselected_*), sem obrigatoriedade.

# 8. Fluxo guiado
Evidências:
- Etapa que chama PT/OS: eventos/views.py, função guiado_etapa_4.
- URL da etapa: /eventos/<evento_id>/guiado/etapa-4/ (eventos/urls.py).
- URLs abertas para cadastro real:
  - eventos:documentos-planos-trabalho-novo com query context_source=evento&preselected_event_id=<id>&return_to=<url_etapa4>
  - eventos:documentos-ordens-servico-novo com query context_source=evento&preselected_event_id=<id>&return_to=<url_etapa4>
- Template da etapa: templates/eventos/guiado/etapa_4.html
  - exibe listas de planos_trabalho e ordens_servico reais vinculadas ao evento.
  - botões Novo PT/Nova OS apontam para as rotas reais de CRUD.

Conclusões:
- Abre o cadastro real: SIM.
- Existe CRUD paralelo de etapa 4: NÃO identificado.
- Retorno por contexto: via query return_to/context_source/preselected_event_id repassada aos forms/templates.

# 9. Geração documental
Serviços alterados:
- eventos/services/documentos/context.py
- eventos/services/documentos/plano_trabalho.py
- eventos/services/documentos/ordem_servico.py

Leitura de modelos PT/OS:
- context.py usa PlanoTrabalho e OrdemServico via:
  - _get_plano_trabalho_for_oficio
  - _get_ordem_servico_for_oficio
- prioridade de leitura:
  - por ofício (PlanoTrabalho.oficio / OrdemServico.oficio)
  - fallback por evento (PlanoTrabalho.evento / OrdemServico.evento)

Leitura de EventoFundamentacao:
- Não há leitura ativa em context.py/plano_trabalho.py/ordem_servico.py no estado atual.

Funções de renderização PT:
- render_plano_trabalho_docx(oficio)
- render_plano_trabalho_model_docx(plano_trabalho)

Funções de renderização OS:
- render_ordem_servico_docx(oficio)
- render_ordem_servico_model_docx(ordem_servico)

# 10. Migração de dados
Migration analisada: eventos/migrations/0031_ordemservico_documentoavulso_ordem_servico_and_more.py

Cria:
- model OrdemServico
- model PlanoTrabalho
- model EfetivoPlanoTrabalhoDocumento
- campo DocumentoAvulso.ordem_servico
- alteração DocumentoAvulso.plano_trabalho para FK de PlanoTrabalho

RunPython executado:
- função migrate_fundamentacao_to_pt_os
  - lê EventoFundamentacao
  - converte cada registro:
    - tipo OS -> OrdemServico (id = id da fundamentação)
    - demais -> PlanoTrabalho (id = id da fundamentação)
  - status derivado por _status_from_fundamentacao(tipo_documento, texto_fundamentacao)
  - migra conteúdo textual e campos correlatos de PT.

Migração de DocumentoAvulso:
- casos OS: move plano_trabalho_id legado para ordem_servico_id e limpa plano_trabalho_id.
- casos órfãos não mapeados: limpa plano_trabalho_id para evitar FK inválida.

Migração de efetivo legado:
- lê EfetivoPlanoTrabalho (por evento) e replica em EfetivoPlanoTrabalhoDocumento, mapeando por evento->plano_trabalho convertido.
- usa update_or_create para evitar duplicação por (plano_trabalho, cargo).

Riscos:
- Risco de duplicidade: baixo na migração de efetivo (há update_or_create + constraint única).
- Risco de perda de dados: existe risco controlado de limpeza de referências órfãs em DocumentoAvulso.plano_trabalho (dados não mapeáveis são nulados por desenho da migration).

# 11. Busca de referências residuais
Busca textual executada para:

EventoFundamentacao:
- Uso de aplicação (não-teste/migração):
  - eventos/models.py: class EventoFundamentacao (residual de domínio).
  - eventos/forms.py: import + EventoFundamentacaoForm (residual/form legado).
  - eventos/admin.py: registro admin (residual administrativo).
  - eventos/views_global.py: _document_status_summary usa evento.fundamentacao (residual e sem chamada identificada).
- Compatibilidade:
  - eventos/migrations/0031...: RunPython de migração de legado.
- Testes:
  - eventos/tests/test_eventos.py
  - eventos/tests/test_global_views.py
  - eventos/tests/test_plano_trabalho.py

plano_trabalho antigo:
- eventos/migrations/0026_ajuste_roteiro_avulso_autogen.py
  - FK antiga para eventos.eventofundamentacao (to='eventos.eventofundamentacao').
  - Classificação: histórico de migração (não uso ativo runtime).
- eventos/migrations/0031...
  - comentário e conversão explícita do vínculo legado.
  - Classificação: compatibilidade/migração.

ordem_servico antiga:
- Não há model legado separado de OS; legado vinha por EventoFundamentacao.tipo_documento == OS.
- Referências encontradas:
  - eventos/models.py: constantes TIPO_OS em EventoFundamentacao (residual de domínio legado).
  - testes legados com EventoFundamentacao.TIPO_OS.
  - eventos/views_global.py: parâmetro fundamentacao_tipo em helper residual.

Resumo por classificação:
- Uso ativo: nenhum no núcleo principal PT/OS (CRUD + guiado etapa 4 + services documentais PT/OS).
- Compatibilidade temporária: migration 0031.
- Código residual/morto: model/form/admin/helper/template de derivado + testes legados.

# 12. Checklist final de verdade
1. Plano de Trabalho existe como model próprio: IMPLEMENTADO
2. Ordem de Serviço existe como model próprio: IMPLEMENTADO
3. PT pode existir sem Evento: IMPLEMENTADO
4. OS pode existir sem Evento: IMPLEMENTADO
5. PT pode existir sem Ofício: IMPLEMENTADO
6. OS pode existir sem Ofício: IMPLEMENTADO
7. PT tem CRUD real: IMPLEMENTADO
8. OS tem CRUD real: IMPLEMENTADO
9. Fluxo guiado só reaproveita cadastro real: IMPLEMENTADO
10. Serviços documentais usam os novos models: IMPLEMENTADO
11. EventoFundamentacao saiu do núcleo ativo: PARCIAL
12. A arquitetura ficou realmente mais document-centric: IMPLEMENTADO

# 13. Problemas remanescentes
- EventoFundamentacao permanece no domínio (models.py), sem descontinuação formal.
- EventoFundamentacaoForm permanece no código, apesar da etapa 4 usar cadastro real PT/OS.
- EventoFundamentacaoAdmin permanece registrado.
- Helper residual _document_status_summary em views_global.py ainda referencia evento.fundamentacao e não possui chamadas encontradas.
- Template residual templates/eventos/global/documento_derivado_lista.html ainda expõe campo fundamentacao_label.
- Testes ainda refletem legado EventoFundamentacao em vários pontos e podem mascarar regressões do novo desenho se não forem atualizados.
- Texto de pendência em views.py (_evento_pendencias_finalizacao) ainda menciona “Preencha tipo e texto da fundamentação.”, sem refletir perfeitamente o novo critério por PT/OS finalizado.

# 14. Veredito final
DESACOPLAMENTO PARCIALMENTE CONCLUÍDO

Justificativa do veredito:
- Concluído no núcleo funcional: models independentes, CRUD real, rotas reais, fluxo guiado consumindo cadastro real e geração documental baseada em PT/OS.
- Parcial na limpeza arquitetural: EventoFundamentacao e artefatos associados ainda existem no código como legado residual (alguns sem uso ativo, mas ainda presentes).