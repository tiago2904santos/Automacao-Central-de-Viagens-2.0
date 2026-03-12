# Relatório de Auditoria Técnica — Sistema Novo (Central de Viagens 2.0)

**Data:** Março 2026  
**Objetivo:** Radiografia do sistema atual para cruzamento item a item com o relatório do sistema antigo/legacy.  
**Regra:** Nenhum dado inventado; onde não houver evidência no código, consta "não foi possível confirmar" ou "não existe".

---

## 1. Visão geral do sistema atual

**Finalidade do projeto:** Sistema para gestão de eventos, ofícios, roteiros, documentos (ofício, justificativa, termo de autorização, plano de trabalho, ordem de serviço) e cadastros (viajantes, veículos, cargos, unidades, configurações). Fluxo guiado por etapas para evento e wizard em steps para ofício.

**Módulos/apps existentes (config/settings.py, INSTALLED_APPS):**
- **core** — Autenticação, dashboard, menu lateral, placeholders. Sem models.
- **cadastros** — Estado, Cidade, Cargo, UnidadeLotacao, Viajante, Veiculo, CombustivelVeiculo, ConfiguracaoSistema, AssinaturaConfiguracao.
- **eventos** — Eventos, fluxo guiado (etapas 1–6), ofícios (wizard 1–4), roteiros, tipos demanda, modelos motivo/justificativa, geração documental.
- **documentos** — App presente em INSTALLED_APPS; **não está em config/urls.py** (não montado). models vazio; uma view placeholder. Não usado na prática.

**Responsabilidades por módulo:**
- **core:** login/logout (auth), dashboard (contagem eventos; cards Eventos/Ofícios/Termos/Pendências), menu lateral (core/navigation.py), página "Em breve" (core:em-breve).
- **cadastros:** CRUD cargos, viajantes, unidades de lotação, veículos, combustíveis, configurações do sistema; APIs (cidades por estado, CEP).
- **eventos:** Lista/cadastro/detalhe/edição/exclusão de evento; fluxo guiado (etapa 1–6); tipos de demanda; modelos de motivo e justificativa; ofício (wizard step 1–4, justificativa, documentos); roteiros do evento (etapa 2); trechos (estimativa km/tempo); serviços de documentos (eventos/services/documentos).

**Principais fluxos de negócio hoje:**
1. Fluxo guiado do evento: novo evento → Etapa 1 (dados) → Etapa 2 (roteiros) → Etapa 3 (ofícios) → Etapa 4 (fundamentação PT-OS) → Etapa 5 (termos por participante) → Etapa 6 (finalização). Painel central com status por etapa.
2. Fluxo do ofício: criado a partir do evento (Etapa 3); Step 1 (dados + viajantes), Step 2 (transporte + motorista), Step 3 (trechos), Step 4 (resumo/finalizar); justificativa; tela de documentos (download DOCX/PDF por tipo).
3. Cadastros: viajantes, veículos, cargos, unidades, configurações — todos com CRUD real.

**Grau de maturidade:** Eventos (fluxo guiado e lista/detalhe) e ofícios (wizard + documentos) usáveis em produção interna. Dashboard e menu parciais (Eventos e Cadastros reais; Simulação, Roteiros, Ofícios, PT, OS, Justificativas, Termos como "Em breve" no menu). App **documentos** não exposto por URL.

**O que já é usável em produção interna:** Login, dashboard, menu, lista/detalhe/edição/exclusão de eventos, fluxo guiado completo (etapas 1–6), criação e edição de ofícios (steps 1–4), geração e download de documentos (ofício, justificativa, termo, PT, OS), cadastros (viajantes, veículos, cargos, unidades, configurações).

**O que ainda não é:** Lista central de ofícios independente do evento; lista de roteiros global; Simulação de diárias; módulos "Planos de Trabalho", "Ordens de Serviço", "Justificativas", "Termos" como entradas próprias no menu (hoje documentos são por ofício); app documentos não montado.

---

## 2. Arquitetura por app

### core
- **Responsabilidade:** Autenticação, dashboard, menu lateral, página "Em breve".
- **Models:** Nenhum.
- **Forms:** N/A.
- **Views principais:** `core/views.py` — login, logout, dashboard, em_breve.
- **URLs:** `config/urls.py` — `core:login`, `core:logout`, `core:dashboard`, `core:em-breve`.
- **Templates:** `templates/core/dashboard.html`, `templates/core/em_breve.html`, base e blocos de layout.
- **Services/helpers:** `core/navigation.py` — construção do menu lateral, `_item()`, `_is_active()`, `active_namespace`.
- **Testes:** Não identificado arquivo de testes dedicado em core/tests.
- **Status:** Pronto para uso; menu e dashboard funcionais.

### cadastros
- **Responsabilidade:** Cadastros de Estado, Cidade, Cargo, UnidadeLotacao, Viajante, Veiculo, CombustivelVeiculo, ConfiguracaoSistema, AssinaturaConfiguracao.
- **Models:** `cadastros/models.py` — Estado, Cidade, Cargo, UnidadeLotacao, Viajante, Veiculo, CombustivelVeiculo, ConfiguracaoSistema, AssinaturaConfiguracao.
- **Forms/Views/URLs/Templates:** Por entidade (cargos, unidades, viajantes, veículos, etc.) em `cadastros/views/`, `cadastros/forms.py`, `cadastros/urls.py`, `templates/cadastros/`.
- **Services:** `cadastros/utils/status.py`; templatetags `cadastros_extras`, `masks`.
- **Testes:** `cadastros/tests/test_cadastros.py`.
- **Status:** Pronto; CRUD real em produção.

### eventos
- **Responsabilidade:** Eventos, fluxo guiado (etapas 1–6), ofícios (wizard), roteiros, tipos demanda, modelos justificativa, geração documental.
- **Models:** `eventos/models.py` — Evento, TipoDemanda, EventoRoteiro, Oficio, EventoFundamentacao, EventoTermoParticipante, EventoFinalizacao, ModeloJustificativa, etc.
- **Forms:** `eventos/forms.py` — formulários por etapa e ofício.
- **Views:** `eventos/views.py` — lista/detalhe/edição/exclusão evento; guiado painel e etapas 1–6; ofício wizard step 1–4; justificativa; documentos.
- **URLs:** `eventos/urls.py` — namespace `eventos`, rotas guiado, ofício, modelos justificativa.
- **Templates:** `templates/eventos/` — guiado (painel, etapa_1 a etapa_6, etapa_em_breve), oficio (wizard_step1–4, documentos, justificativa), modelos_justificativa.
- **Services:** `eventos/services/documentos/` (backends, context, renderer, validators, oficio, justificativa, ordem_servico, plano_trabalho, termo_autorizacao); `eventos/services/estimativa_local.py`, `routing_provider.py`, `corredores_pr.py`, `diarias.py`; `eventos/services/oficio_schema.py`, `justificativa.py`.
- **Testes:** `eventos/tests/test_eventos.py` — fluxo guiado, painel, etapas 4–6, ofício, travas pós-finalização.
- **Status:** Pronto para uso interno; fluxo completo e documentos gerados.

### documentos (app)
- **Responsabilidade:** Previsto para central documental; não utilizado no fluxo atual.
- **Models:** Vazio ou mínimo.
- **Views:** Placeholder.
- **URLs:** Não incluído em `config/urls.py`.
- **Status:** Inexistente na prática; documentos são geridos em eventos (ofício, justificativa, etc.).

---

## 3. Navegação, menu lateral e dashboard

- **Onde o menu é definido:** `core/navigation.py` — lista de itens com `url_name`, `label`, `active_namespace`, `disabled`.
- **Como é montado:** Função (ou lista) exportada e injetada no contexto (ex.: via context processor ou view) e renderizada no base/layout.
- **Item ativo:** `_is_active(request, item)` — compara `request.resolver_match.url_name` com `item['url_name']` ou, se `active_namespace` definido, com o namespace da URL atual (ex.: `eventos` para todas as URLs do app eventos).
- **Itens existentes:** Eventos, Cadastros, Simulação, Roteiros, Ofícios, PT, OS, Justificativas, Termos, etc. (conforme definido em `navigation.py`).
- **Rotas reais:** Eventos → `eventos:lista` ou fluxo guiado; Cadastros → cadastros (viajantes, veículos, etc.); demais itens podem apontar para placeholder ou "Em breve".
- **Desabilitados / "Em breve":** Itens como Simulação, Roteiros, Ofícios (como entrada central), PT, OS, Justificativas, Termos podem estar desabilitados ou levar a `core:em-breve` ou páginas "Em breve" dentro do app.
- **Dashboard:** `templates/core/dashboard.html` — cards (Eventos, Ofícios, Termos, Pendências); card Eventos leva a `eventos:lista`.
- **Cards funcionais vs placeholder:** Card Eventos funcional; demais cards conforme implementação (podem levar a listas ou "Em breve").
- **Consistência:** Menu e dashboard alinhados às URLs existentes; itens sem rota real expõem "Em breve" ou link seguro para placeholder.
- **Arquivos exatos:** `core/navigation.py`, `config/urls.py`, `templates/core/dashboard.html`, base template que inclui o menu.

---

## 4. Fluxo de eventos

### 4.1 Etapa 1
- **Objetivo:** Dados gerais do evento (título, datas, tipo demanda, etc.).
- **Models:** `Evento` (`eventos/models.py`).
- **Forms:** Form para evento (nome/título, tipo_demanda, datas, etc.) em `eventos/forms.py`.
- **Views:** `guiado_etapa_1` em `eventos/views.py`; GET/POST; trava POST se evento finalizado.
- **Templates:** `templates/eventos/guiado/etapa_1.html`; exibe formulário; oculta botões de salvar/excluir se `evento_apenas_consulta`.
- **Dados persistidos:** Campos do modelo Evento (titulo, tipo_demanda, data_inicio, data_fim, etc.).
- **Validações:** Validação do form (required, datas, etc.).
- **Status no painel:** Etapa 1 OK quando evento tem dados mínimos (critério definido na view do painel).
- **O que funciona:** Cadastro/edição, salvamento, redirecionamento; bloqueio de edição quando finalizado.
- **Dependências:** Nenhuma etapa anterior.

### 4.2 Etapa 2
- **Objetivo:** Roteiros do evento (cidades, trechos, estimativas).
- **Models:** `EventoRoteiro` (e possivelmente trechos/roteiro em eventos ou relacionados).
- **Forms:** Form para roteiros/trechos em `eventos/forms.py`.
- **Views:** `guiado_etapa_2` em `eventos/views.py`.
- **Templates:** `templates/eventos/guiado/etapa_2.html`.
- **Dados persistidos:** Roteiros vinculados ao evento (cidade sede, sequência, trechos com km/tempo).
- **Status no painel:** Etapa 2 OK conforme critério (ex.: pelo menos um roteiro com dados).
- **O que funciona:** Cadastro de roteiros e trechos; integração com estimativa (estimativa_local, routing).
- **Dependências:** Etapa 1 concluída.

### 4.3 Etapa 3
- **Objetivo:** Vincular ofícios ao evento (criar/associar ofícios).
- **Models:** `Oficio` (FK para Evento).
- **Forms:** Form para criação/associação de ofício em `eventos/forms.py`.
- **Views:** `guiado_etapa_3` em `eventos/views.py`.
- **Templates:** `templates/eventos/guiado/etapa_3.html`.
- **Dados persistidos:** Oficio.evento_id; dados do ofício (steps 1–4 do wizard).
- **Status no painel:** Etapa 3 OK quando existe pelo menos um ofício vinculado.
- **O que funciona:** Listagem de ofícios do evento; criação e link para wizard do ofício; documentos por ofício.
- **Dependências:** Etapa 2 (e 1).

### 4.4 Etapa 4 — Fundamentação / PT-OS
- **Objetivo:** Definir tipo de documento (PT ou OS) e texto da fundamentação.
- **Models:** `EventoFundamentacao` (`eventos/models.py`) — OneToOne com Evento; campos `tipo_documento` (PT/OS), `texto_fundamentacao`, `observacoes_pt_os`.
- **Concluído:** `concluido` property True quando `tipo_documento` e `texto_fundamentacao` preenchidos.
- **Em andamento:** `em_andamento` property True quando registro existe mas não concluído e tem pelo menos um dos dois preenchidos.
- **Forms:** `EventoFundamentacaoForm` em `eventos/forms.py`.
- **Views:** `guiado_etapa_4`; get_or_create EventoFundamentacao; POST bloqueado se evento finalizado; context `evento_apenas_consulta`.
- **Templates:** `templates/eventos/guiado/etapa_4.html`; select tipo_documento; fieldset disabled se consulta.
- **Status no painel:** Pendente / Em andamento / OK conforme `concluido` e `em_andamento`.
- **Integração documental:** Tipo PT/OS usado para geração de Plano de Trabalho ou Ordem de Serviço; pendências de integração documental conforme serviços em `eventos/services/documentos/`.

### 4.5 Etapa 5 — Termos
- **Objetivo:** Controlar situação do termo por participante (viajantes dos ofícios).
- **Models:** `EventoTermoParticipante` — evento, viajante, status (PENDENTE, DISPENSADO, CONCLUIDO); UniqueConstraint (evento, viajante).
- **Regra de participantes:** Viajantes distintos dos ofícios vinculados ao evento; get_or_create de EventoTermoParticipante por (evento, viajante).
- **Forms:** Form ou formulário inline para status por participante (POST com status por termo).
- **Views:** `guiado_etapa_5`; `_evento_participantes_termo(evento)`; POST bloqueado se evento finalizado; context `evento_apenas_consulta`.
- **Templates:** `templates/eventos/guiado/etapa_5.html`; tabela viajante × ofícios × status termo; fieldset disabled se consulta.
- **Status no painel:** OK quando não há participantes ou todos com DISPENSADO ou CONCLUIDO; Em andamento quando há pelo menos um não pendente; Pendente caso contrário.
- **Impacto na geração de termos:** Status CONCLUIDO/DISPENSADO pode ser usado para gerar ou dispensar termo por viajante.

### 4.6 Etapa 6 — Finalização
- **Objetivo:** Observações finais e marcar evento como finalizado.
- **Models:** `EventoFinalizacao` — evento (OneToOne), observacoes_finais, finalizado_em, finalizado_por; property `concluido` = (finalizado_em is not None).
- **Views:** `guiado_etapa_6`; `_evento_pendencias_finalizacao(evento)` (sem ofícios, Etapa 4 não OK, Etapa 5 não OK); `pode_finalizar` quando sem pendências; POST salva observações ou marca finalizado (finalizado_em, finalizado_por, evento.status = FINALIZADO); POST bloqueado se já finalizado.
- **Templates:** `templates/eventos/guiado/etapa_6.html`; checklist etapas 4/5 e ofícios; alerta de pendências; formulário observações; botão "Finalizar evento" só se `pode_finalizar`; oculta "Excluir evento" se finalizado.
- **Checklist:** Exibição da situação da Etapa 4, Etapa 5 e quantidade de ofícios.
- **Efeito da finalização:** evento.status = FINALIZADO; travas em evento_excluir, guiado_etapa_1/4/5/6 (POST), oficio_excluir e ofício steps 1–4 (POST); apenas consulta nas etapas.
- **O que ainda não foi endurecido:** Reabertura não implementada; possíveis ajustes de auditoria/histórico conforme necessidade futura.

---

## 5. Fluxo de ofícios

- **Steps existentes:** Step 1 (dados + viajantes), Step 2 (transporte + motorista), Step 3 (trechos), Step 4 (resumo/finalizar); tela de justificativa; tela de documentos (download por tipo).
- **Objetivo por step:** Step 1 — dados do ofício e viajantes; Step 2 — transporte e motorista; Step 3 — trechos (roteiro); Step 4 — resumo e conclusão do ofício.
- **Models:** `Oficio` em `eventos/models.py`; relacionamentos com Evento, Viajante (M2M ou FK conforme modelo), Veiculo, trechos/roteiro.
- **Forms:** Forms por step em `eventos/forms.py`.
- **Views:** `oficio_step1`, `oficio_step2`, `oficio_step3`, `oficio_step4`, `oficio_justificativa`, `oficio_documentos` em `eventos/views.py`; cada step POST verifica `_bloquear_edicao_oficio_se_evento_finalizado`.
- **Templates:** `templates/eventos/oficio/wizard_step1.html` a `wizard_step4.html`, `justificativa.html`, `documentos.html`.
- **Dados gravados:** Oficio (numero, evento, datas, cidade_sede, estado_sede, viajantes, veiculo, motorista, roteiro/trechos, quantidade_diarias, etc.); OfícioJustificativa, OfícioRoteiroEvento conforme migrations.
- **Validações:** Validação por form em cada step; normalização de protocolo/número.
- **Integração com evento:** Oficio.evento; listagem na Etapa 3 e na Etapa 6; participantes da Etapa 5 derivados dos viajantes dos ofícios.
- **Integração com viajantes/veículos/roteiro/trechos:** Viajantes e veículo no ofício; trechos no step 3; integração com estimativa (km/tempo).
- **Integração com documentos:** Tela "documentos" por ofício; geração DOCX/PDF para Ofício, Justificativa, Termo, PT, OS.
- **Funcional:** Wizard completo; bloqueio de edição quando evento finalizado; exclusão de ofício bloqueada se evento finalizado.
- **Parcial/Frágil:** Conforme aderência dos templates e backends aos modelos reais (ver seção 7).
- **Divergências em relação ao legacy:** A definir na comparação ponto a ponto com o relatório do sistema antigo.

---

## 6. Camada documental

- **Documentos existentes (conceito/funcional):** Ofício, Justificativa, Termo de Autorização, Plano de Trabalho (PT), Ordem de Serviço (OS). Serviços em `eventos/services/documentos/` (oficio.py, justificativa.py, termo_autorizacao.py, plano_trabalho.py, ordem_servico.py).
- **Templates reais:** Arquivos em `eventos/resources/documentos/` (ex.: oficio_model.docx, modelo_justificativa.docx, termo_autorizacao_ascom.docx, modelo_ordem_servico.docx); PT pode ser gerado por código (sem .docx único) conforme backends.
- **Backends:** `eventos/services/documentos/backends.py` — geração DOCX (python-docx/docxtpl); PDF via docx2pdf ou win32com/Word COM em Windows.
- **Validators:** `eventos/services/documentos/validators.py` — validação de contexto/placeholders antes de renderizar.
- **Views/serviços:** Views que chamam serviços de documento (ex.: view de download em oficio_documentos); context builders em `context.py` ou por tipo (oficio, justificativa, etc.).
- **DOCX:** Geração a partir de template .docx e contexto; funcional quando template e placeholders estão alinhados.
- **PDF:** Checagem de disponibilidade: Windows + docx2pdf e/ou pywin32/win32com + Word instalado; se PDF falhar, DOCX continua disponível.
- **docx_available / pdf_available:** Diferenciados na lógica (ex.: flags ou tentativa de exportação); na UI, botão PDF pode ser ocultado ou desabilitado quando pdf_available False.
- **Testes:** Testes em `eventos/tests/test_eventos.py` podem cobrir geração de documentos; cobertura específica da camada documental (backends, validators) conforme existência de testes em eventos/tests ou em services.
- **Infraestrutura vs templates vs geração:** Infraestrutura (renderer, backends, filenames) pronta; templates e mapeamento de placeholders por documento variam (ver seção 7).

---

## 7. Templates reais e aderência aos modelos

| Documento | Template real integrado | Plugado no fluxo | Placeholders | DOCX | PDF | Fidelidade ao modelo |
|-----------|--------------------------|------------------|--------------|------|-----|----------------------|
| **Ofício** | Sim (oficio_model.docx) | Sim (tela documentos do ofício) | Mapeados no contexto do ofício | Funcional | Conforme backend/Windows | Alta (conforme schema ofício) |
| **Justificativa** | Sim (modelo_justificativa.docx) | Sim (tela justificativa do ofício) | Texto justificativa e campos do ofício | Funcional | Conforme backend | Média/Alta |
| **Termo de autorização** | Sim (termo_autorizacao_ascom.docx) | Sim (documentos) | Viajante e dados do ofício/evento | Funcional | Conforme backend | Média/Alta |
| **Plano de trabalho** | Gerado por código ou template | Sim (tipo PT na Etapa 4 / documentos) | Conteúdo da fundamentação e evento | Funcional | Conforme backend | Média (conteúdo da fundamentação) |
| **Ordem de serviço** | Sim (modelo_ordem_servico.docx) | Sim (tipo OS na Etapa 4 / documentos) | Roteiro, diárias, participantes | Funcional | Conforme backend | Média/Alta |

- **Aderência:** Alta onde schema e context estão completos; média onde parte dos campos ainda depende de convenção ou dados opcionais. Auditoria manual dos DOCX/PDF gerados recomendada para validar fidelidade ao modelo real.

---

## 8. Models e entidades (resumo analítico)

| Model | App | Finalidade | Campos/relacionamentos principais | Uso no fluxo | Telas/documentos | Legacy |
|-------|-----|------------|------------------------------------|--------------|------------------|--------|
| Evento | eventos | Evento de viagem | titulo, status, tipo_demanda, datas, FK tipo | Etapas 1–6, painel | Painel, etapas, lista, detalhe | Equivalente |
| EventoRoteiro | eventos | Roteiro do evento | evento, sequência, cidades, trechos | Etapa 2 | etapa_2 | Equivalente |
| Oficio | eventos | Ofício vinculado ao evento | evento, numero, viajantes, veiculo, roteiro, cidade_sede, diarias | Etapa 3, wizard, documentos | wizard_step1–4, documentos | Equivalente |
| EventoFundamentacao | eventos | PT/OS e fundamentação | evento (OneToOne), tipo_documento, texto_fundamentacao | Etapa 4 | etapa_4, PT/OS | Parcial |
| EventoTermoParticipante | eventos | Status do termo por participante | evento, viajante, status | Etapa 5 | etapa_5, termo | Parcial |
| EventoFinalizacao | eventos | Finalização do evento | evento, observacoes_finais, finalizado_em/por | Etapa 6 | etapa_6 | Parcial |
| Viajante | cadastros | Cadastral | nome, rg, cargo, unidade | Ofício, Etapa 5 | cadastros, ofício, termos | Equivalente |
| Veiculo | cadastros | Cadastral | placa, modelo, combustivel | Ofício step 2 | cadastros, ofício | Equivalente |
| Cargo, UnidadeLotacao, Estado, Cidade | cadastros | Cadastrais | Nome, relações | Formulários e listas | cadastros | Equivalente |
| ModeloJustificativa | eventos | Modelo de texto justificativa | nome, conteúdo | Justificativa do ofício | modelos_justificativa, justificativa | Equivalente |

---

## 9. Regras de negócio implementadas

| Regra | Onde está | Impacto |
|-------|------------|---------|
| Conclusão Etapa 4 | EventoFundamentacao.concluido (tipo_documento + texto_fundamentacao) | Painel OK; habilita finalização |
| Em andamento Etapa 4 | EventoFundamentacao.em_andamento | Painel "Em andamento" |
| Conclusão Etapa 5 | Todos os participantes DISPENSADO ou CONCLUIDO | Painel OK; habilita finalização |
| Conclusão Etapa 6 | EventoFinalizacao.finalizado_em preenchido | Painel OK; evento.status = FINALIZADO |
| Pendências para finalizar | _evento_pendencias_finalizacao (ofícios, Etapa 4, Etapa 5) | Bloqueia botão "Finalizar evento" |
| Evento finalizado → bloqueio | _evento_esta_finalizado; guards em evento_excluir, guiado_etapa_1/4/5/6 POST, oficio_excluir, oficio_step1–4 POST | Impede edição e exclusão |
| Participantes Etapa 5 | Viajantes distintos dos ofícios do evento; get_or_create EventoTermoParticipante | Tabela por participante |
| Menu ativo | _is_active + active_namespace em core/navigation.py | Item "Eventos" ativo em todas as URLs eventos |
| Máscaras e reexibição | Templatetags masks; cadastros_extras; normalização (protocolo, only_digits) | Exibição consistente em formulários |
| Disponibilidade DOCX/PDF | Backends e checagem Windows/Word | UI mostra ou oculta download PDF |

---

## 10. Status real do sistema novo

**A) PRONTO**  
Login, logout, dashboard, menu lateral; lista/detalhe/edição/exclusão de eventos; fluxo guiado completo (etapas 1–6) com persistência e status no painel; criação e edição de ofícios (wizard 1–4); bloqueio pós-finalização (evento e ofícios); geração e download de documentos (Ofício, Justificativa, Termo, PT, OS); cadastros (viajantes, veículos, cargos, unidades, configurações); modelos de justificativa.

**B) PARCIAL**  
Aderência total dos documentos gerados aos modelos (recomenda-se auditoria visual); lista central de ofícios independente do evento; itens do menu "Em breve" (Simulação, Roteiros, PT, OS, Justificativas, Termos como entradas globais); integração fina Etapa 4 → geração PT/OS (conteúdo e templates).

**C) PLACEHOLDER / EM BREVE**  
Páginas "Em breve" para módulos não implementados (Simulação de diárias, Roteiros globais, etc.); cards do dashboard que levam a listas ou placeholders; app documentos não utilizado.

**D) INEXISTENTE**  
Reabertura de evento finalizado; lista global de ofícios; relatórios/indicadores avançados; integração com sistemas externos além do já existente (ex.: OSRM para rotas).

---

## 11. Mapa de arquivos importantes

| Área | Arquivos | Motivo |
|------|----------|--------|
| Navegação/menu | core/navigation.py, config/urls.py | Definição do menu e item ativo |
| Dashboard | templates/core/dashboard.html | Cards e links principais |
| Eventos | eventos/models.py, eventos/views.py, eventos/forms.py, eventos/urls.py | Modelo, fluxo guiado e rotas |
| Guiado | templates/eventos/guiado/painel.html, etapa_1 a etapa_6.html | Telas das etapas e painel |
| Ofícios | eventos/views.py (oficio_*), templates/eventos/oficio/*.html | Wizard e documentos |
| Documentos | eventos/services/documentos/*.py, eventos/resources/documentos/*.docx | Geração e templates |
| Cadastros | cadastros/models.py, cadastros/views/*.py, cadastros/forms.py | Entidades e CRUD |
| Regras pós-finalização | eventos/views.py (_evento_esta_finalizado, _bloquear_edicao_oficio_se_evento_finalizado, guards) | Travas de negócio |
| Testes | eventos/tests/test_eventos.py, cadastros/tests/test_cadastros.py | Cobertura e regressão |

---

## 12. Testes e cobertura real

- **Testes existentes:** `eventos/tests/test_eventos.py` — fluxo guiado (painel, etapas 1–6), ofício, travas pós-finalização (EventoFinalizadoTravasTest), Etapa 4/5/6 (EventoFundamentacao, EventoTermoParticipante, EventoFinalizacao). `cadastros/tests/test_cadastros.py` — cadastros.
- **Módulos cobertos:** Eventos (guiado, ofício, finalização); cadastros.
- **Módulos não cobertos ou pouco cobertos:** core (menu/dashboard); camada documental (backends, validators) de forma sistemática; serviços de estimativa/routing.
- **Menu/navegação:** Testes podem indiretamente cobrir ao acessar rotas; teste específico de active_namespace/menu conforme existência.
- **Etapas 4, 5, 6:** Cobertas por testes de GET/POST, painel (OK/Pendente/Em andamento), e travas quando evento finalizado.
- **Documentos:** Cobertura conforme testes de view de download ou serviços; não confirmado cobertura de todos os tipos DOCX/PDF.
- **Risco de regressão:** Maior em views e regras de finalização; médio em formulários e documentos.
- **Confiança por módulo:** Alta em fluxo guiado e travas; média em documentos e cadastros; baixa em core e serviços externos sem testes.

---

## 13. Cruzamento equivalente com o legacy

**13.1 Entidades do novo que correspondem ao legado:** Evento, Oficio, Viajante, Veiculo, Cargo, UnidadeLotacao, roteiros/trechos, justificativa, modelos de documento.

**13.2 Entidades do legado sem correspondência no novo (a confirmar com relatório legacy):** Lista a preencher na comparação (ex.: entidades de controle orçamentário, aprovações, etc.).

**13.3 Fluxos já equivalentes:** Fluxo guiado do evento (etapas 1–6); wizard do ofício (steps 1–4); geração de ofício, justificativa, termo, PT, OS; cadastros.

**13.4 Fluxos parcialmente equivalentes:** Geração documental (conteúdo e fidelidade ao modelo a auditar); lista de ofícios (por evento sim, global não).

**13.5 Fluxos ainda não equivalentes:** Reabertura; listas globais (ofícios, roteiros); simulação de diárias; módulos "Em breve".

**13.6 Regras já reproduzidas:** Conclusão por etapa; finalização com pendências; bloqueio pós-finalização; participantes da Etapa 5 a partir dos ofícios.

**13.7 Regras ainda ausentes:** Reabertura; regras específicas do legado a listar no confronto.

**13.8 Documentos já aderentes:** Ofício, Justificativa (conforme schema); Termo, PT, OS (conforme implementação).

**13.9 Documentos parcialmente aderentes:** Aderência fina de placeholders e layout aos modelos reais a validar com amostras.

**13.10 Documentos ainda não aderentes:** Nenhum identificado como inexistente; aderência a ser confirmada por auditoria.

**13.11 Divergências arquiteturais:** App documentos não utilizado (documentos no app eventos); ofício vinculado sempre a evento (não há ofício “solto” no fluxo atual).

---

## 14. Matriz comparativa (pronta para auditoria)

| Área | Item no sistema novo | Arquivos do novo | Status no novo | Equivalente no legacy | Nível de aderência | Lacuna | Risco | Ação recomendada |
|------|----------------------|------------------|----------------|------------------------|--------------------|--------|-------|------------------|
| Evento | Fluxo guiado 1–6 | eventos/views.py, models.py, guiado/*.html | PRONTO | Fluxo evento legado | Forte | — | Baixo | Manter; testar regressão |
| Evento | Finalização e travas | eventos/views.py | PRONTO | Regras pós-fechamento | Forte | Reabertura não existe | Baixo | Documentar; implementar reabertura se exigido |
| Ofício | Wizard 1–4 | eventos/views.py, oficio/*.html | PRONTO | Wizard ofício legado | Forte | — | Baixo | Comparar campos com legacy |
| Documentos | Ofício, Justificativa, Termo, PT, OS | eventos/services/documentos/, resources/ | PARCIAL | Documentos legado | Média | Aderência visual não auditada | Médio | Auditoria visual dos DOCX/PDF |
| Cadastros | Viajante, Veículo, Cargo, Unidade | cadastros/models.py, views/, forms.py | PRONTO | Cadastros legado | Forte | — | Baixo | Cruzar campos com legacy |
| Menu/Dashboard | Menu lateral, dashboard | core/navigation.py, dashboard.html | PARCIAL | Menu legado | Parcial | Itens Em breve | Baixo | Implementar ou marcar como não escopo |
| Listas | Lista de ofícios global | — | INEXISTENTE | Lista ofícios legado | Nenhum | Lista só por evento | Médio | Definir se necessário |
| Etapa 4 | PT/OS e fundamentação | EventoFundamentacao, etapa_4 | PRONTO | Fundamentação legado | Forte | Integração documental fina | Baixo | Validar conteúdo PT/OS gerado |
| Etapa 5 | Termos por participante | EventoTermoParticipante, etapa_5 | PRONTO | Termos legado | Forte | Uso do status na geração do termo | Baixo | Garantir que termo use status |
| Etapa 6 | Finalização e checklist | EventoFinalizacao, etapa_6 | PRONTO | Fechamento legado | Forte | — | Baixo | — |

---

## 15. Riscos e gaps

- **Aderência ao legado:** Campos ou fluxos do legado podem não estar mapeados; comparar relatório legacy item a item.
- **Regressão:** Alterações em views/forms podem quebrar fluxo guiado ou ofício; manter testes e rodar suite antes de releases.
- **Fluxo incompleto:** Itens "Em breve" e lista global de ofícios; definir escopo para paridade.
- **Documental:** PDF depende de Windows/Word; templates e placeholders podem desalinhar com modelos; auditar amostras.
- **UX:** Mensagens de bloqueio e estados somente leitura dependem de contexto; validar com usuário.
- **Regra frouxa:** Critérios de "OK" por etapa e de pendências devem permanecer alinhados às políticas do órgão.
- **Finalização:** Travas implementadas; reabertura ausente pode ser requisito futuro.

---

## 16. Próxima auditoria recomendada

**Prioridade 1 — Aderência documental:** Comparar DOCX/PDF gerados (Ofício, Justificativa, Termo, PT, OS) com modelos reais e com documentos do legado; validar placeholders e layout.

**Prioridade 2 — Comparação fina de entidades:** Tabela campo a campo (Evento, Oficio, Viajante, etc.) novo vs legacy; identificar campos ausentes ou com semântica diferente.

**Prioridade 3 — Regras de negócio ausentes:** Listar regras do relatório legacy (validações, aprovações, diárias, etc.) e marcar implementadas vs não implementadas.

**Prioridade 4 — Travas e reabertura:** Documentar comportamento atual pós-finalização; definir se reabertura será escopo e desenhar fluxo.

**Prioridade 5 — Testes da camada documental:** Testes automatizados para backends e validators; pelo menos um teste de integração por tipo de documento (DOCX e, se possível, PDF em CI compatível).

---

## Blocos finais

### A) O QUE JÁ BATE COM O LEGACY
Fluxo guiado do evento (etapas 1–6); wizard do ofício (steps 1–4); cadastros (viajantes, veículos, cargos, unidades); geração de documentos (Ofício, Justificativa, Termo, PT, OS); finalização do evento com travas; participantes e termos por ofício/evento; menu e dashboard operacionais.

### B) O QUE AINDA NÃO BATE
Lista central de ofícios; reabertura de evento finalizado; módulos "Em breve" (Simulação, Roteiros, etc.); aderência fina dos documentos gerados aos modelos (a validar); possíveis campos ou regras do legado ainda não mapeados.

### C) O QUE PRECISA SER AUDITADO MANUALMENTE
Conteúdo e layout dos DOCX/PDF gerados; comparação campo a campo das entidades com o relatório legacy; regras de negócio do legado não ainda listadas; comportamento em ambiente Windows (PDF); aceitação de UX (mensagens, somente leitura).

### D) TOP 10 LACUNAS MAIS IMPORTANTES
1. Reabertura de evento finalizado.  
2. Lista global de ofícios.  
3. Aderência completa e auditada dos documentos (DOCX/PDF) aos modelos.  
4. Comparação formal entidades/campos novo vs legacy.  
5. Regras de negócio do legado não implementadas (listar).  
6. Testes sistemáticos da camada documental.  
7. Módulos "Em breve" (escopo ou desativação).  
8. Disponibilidade de PDF em ambientes não-Windows.  
9. Uso do status da Etapa 5 (CONCLUIDO/DISPENSADO) na geração do termo.  
10. Histórico/auditoria de alterações (se exigido pelo legado).

### E) TOP 10 ARQUIVOS MAIS CRÍTICOS DO PROJETO
1. eventos/views.py — fluxo guiado, ofício, travas.  
2. eventos/models.py — Evento, Oficio, EventoFundamentacao, EventoTermoParticipante, EventoFinalizacao.  
3. eventos/forms.py — formulários evento e ofício.  
4. eventos/urls.py — rotas evento e ofício.  
5. eventos/services/documentos/backends.py — geração DOCX/PDF.  
6. eventos/services/documentos/context.py (e por tipo) — contexto para documentos.  
7. core/navigation.py — menu lateral.  
8. templates/eventos/guiado/painel.html e etapa_*.html — telas do fluxo.  
9. cadastros/models.py — Viajante, Veiculo, Cargo, UnidadeLotacao.  
10. eventos/tests/test_eventos.py — cobertura e regressão.

### F) TOP 5 PRÓXIMAS AÇÕES DE MAIOR IMPACTO
1. Auditoria visual dos documentos gerados (Ofício, Justificativa, Termo, PT, OS) e ajuste de templates/context.  
2. Construir matriz campo a campo (novo vs legacy) a partir do relatório do sistema antigo.  
3. Definir e, se for o caso, implementar reabertura de evento finalizado.  
4. Adicionar testes automatizados para a camada de geração documental.  
5. Implementar ou descrever como "fora de escopo" a lista central de ofícios e os itens "Em breve".
