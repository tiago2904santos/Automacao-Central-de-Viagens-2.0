# Relatório de Auditoria Documental — Central de Viagens 2.0

**Data:** Março 2026  
**Escopo:** Camada documental e aderência dos 5 tipos de documento aos modelos reais.  
**Regras:** Nenhuma alteração no fluxo dos Steps 1–4 do ofício nem nas Etapas 1–6 do evento.

---

## 1. Fase 1 — Mapeamento da implementação atual

### 1.1 Arquitetura documental

| Componente | Localização | Função |
|------------|-------------|--------|
| **Views** | `eventos/views.py` | `oficio_documentos` (tela), `oficio_documento_download` (GET), `_download_oficio_documento`, `_build_oficio_documentos_context` |
| **Services** | `eventos/services/documentos/` | `oficio.py`, `justificativa.py`, `termo_autorizacao.py`, `plano_trabalho.py`, `ordem_servico.py` — cada um expõe `render_*_docx(oficio)` e builders de contexto de template |
| **Context builders** | `eventos/services/documentos/context.py` | `_build_common_context(oficio)`, `build_*_document_context(oficio)` por tipo; `get_assinaturas_documento(tipo)` |
| **Validators** | `eventos/services/documentos/validators.py` | `validate_oficio_for_document_generation(oficio, tipo_documento)`, `get_document_generation_status(oficio, tipo, formato)` |
| **Renderer** | `eventos/services/documentos/renderer.py` | `render_docx_template_bytes`, `safe_replace_placeholders`, `extract_placeholders_from_doc`, `convert_docx_bytes_to_pdf_bytes`, `_render_document_docx_bytes`, `render_document_bytes` |
| **Backends** | `eventos/services/documentos/backends.py` | `get_docx_backend_availability()`, `get_pdf_backend_availability()`, `_load_docx_backend`, `_load_pdf_backend` (docx2pdf + pywin32/Word COM no Windows) |
| **Types** | `eventos/services/documentos/types.py` | `DocumentoOficioTipo`, `DocumentoFormato`, `get_document_type_meta`, registry com `implemented_formats` por tipo |
| **Filenames** | `eventos/services/documentos/filenames.py` | `build_document_filename(oficio, tipo_documento, formato)` |

### 1.2 Templates DOCX reais

| Tipo | Arquivo | Caminho |
|------|---------|---------|
| OFICIO | oficio_model.docx | eventos/resources/documentos/ |
| JUSTIFICATIVA | modelo_justificativa.docx | eventos/resources/documentos/ |
| TERMO_AUTORIZACAO | termo_autorizacao_ascom.docx | eventos/resources/documentos/ |
| PLANO_TRABALHO | — | Gerado por código (create_base_document + helpers no renderer) |
| ORDEM_SERVICO | modelo_ordem_servico.docx | eventos/resources/documentos/ |

### 1.3 Placeholders por template (extraídos do .docx)

- **oficio_model.docx:** armamento, assunto_linha, assunto_oficio, assunto_termo, cargo_chefia, col_cargo, col_ida_chegada, col_ida_saida, col_rgcpf, col_servidor, col_solicitacao, col_volta_chegada, col_volta_saida, combustivel, custo, data_do_oficio, destinos_bloco, diaria, diarias_x, divisao, email, endereco, motivo, motorista_formatado, nome_chefia, oficio, orgao_destino, placa, protocolo, telefone, tipo_viatura, unidade, unidade_rodape, valor_extenso, viatura  
- **modelo_justificativa.docx:** assinante_justificativa, cargo_assinante_justificativa, data_extenso, divisao, email, endereco, justificativa, sede, telefone, unidade, unidade_rodape  
- **termo_autorizacao_ascom.docx:** data_do_evento, destino, divisao, email, endereco, telefone, unidade, unidade_rodape  
- **modelo_ordem_servico.docx:** cargo_chefia, data_extenso, destino, divisao, email, endereco, equipe_deslocamento, motivo, nome_chefia, ordem_de_servico, sede, telefone, unidade, unidade_rodape  

### 1.4 Critérios de disponibilidade DOCX/PDF

- **DOCX:** `get_docx_backend_availability()` — exige `python-docx` instalado.  
- **PDF:** `get_pdf_backend_availability()` — exige Windows, `docx2pdf`, `pywin32`, Word/COM disponível; checagem via `_check_word_com_availability()`.  
- Na UI, DOCX e PDF são tratados separadamente; se PDF falhar, DOCX continua disponível.

---

## 2. Fase 2 — Modelos reais encontrados

| Documento | Modelo real | Observação |
|-----------|-------------|------------|
| Ofício | oficio_model.docx | Único .docx de ofício em eventos/resources/documentos/ |
| Justificativa | modelo_justificativa.docx | Único .docx de justificativa |
| Termo de autorização | termo_autorizacao_ascom.docx | Único .docx de termo; conteúdo adicional via post_processor no código |
| Plano de trabalho | Nenhum .docx | Gerado por código (create_base_document + seções); mantido assim |
| Ordem de serviço | modelo_ordem_servico.docx | Único .docx de OS |

---

## 3. Fase 3 — Auditoria de aderência por documento

### 3.1 OFÍCIO

| Item | Status | Observação |
|------|--------|------------|
| Placeholders do template | Aderente | Todos os placeholders do oficio_model.docx são preenchidos pelo `build_oficio_template_context` |
| Telefone institucional | **Divergência MÉDIA** | Template tem `telefone`; o mapping não enviava — **corrigido**: incluído `telefone` do context institucional |
| Demais campos | OK | numero_formatado, datas, protocolo, chefia, unidade, veículo, motorista, custo, diárias, colunas (servidor, RG/CPF, cargo, ida/volta), motivo, endereço, etc. |

### 3.2 JUSTIFICATIVA

| Item | Status | Observação |
|------|--------|------------|
| Placeholders | **Divergência MÉDIA** | Template tem `telefone`; não era enviado — **corrigido**: incluído no `build_justificativa_template_context` |
| Demais campos | OK | sede, data_extenso, justificativa, assinante, cargo, divisao, unidade, endereco, email |

### 3.3 TERMO DE AUTORIZAÇÃO

| Item | Status | Observação |
|------|--------|------------|
| Placeholders | OK | data_do_evento, destino, divisao, email, endereco, telefone, unidade, unidade_rodape já enviados |
| Conteúdo pós-processado | OK | Parágrafos específicos (“Eu manifesto…”, “Viatura: Modelo:”, “Placa / Combustível:”, “Autorização da Chefia:”) preenchidos pelo `_post_process_termo` |

### 3.4 PLANO DE TRABALHO

| Item | Status | Observação |
|------|--------|------------|
| Modelo | Sem .docx | Gerado por código; estrutura fixa (título, identificação, objetivo, participantes, roteiro, transporte, diárias, assinaturas) |
| Objetivo / fundamentação | **Divergência MÉDIA** | Antes só usava `oficio.motivo`. **Ajuste:** quando o evento tem `EventoFundamentacao` com `tipo_documento == PT`, passa a usar `texto_fundamentacao`; caso contrário mantém `oficio.motivo` |
| PDF | **Divergência BAIXA** | Tipo estava só DOCX. **Ajuste:** PLANO_TRABALHO passou a ter `implemented_formats=(DOCX, PDF)` para paridade com os demais quando o ambiente permite PDF |

### 3.5 ORDEM DE SERVIÇO

| Item | Status | Observação |
|------|--------|------------|
| Placeholders | **Divergência MÉDIA** | Template tem `telefone`; não era enviado — **corrigido**: incluído no `build_ordem_servico_template_context` |
| Finalidade | **Divergência MÉDIA** | Antes só `oficio.motivo`. **Ajuste:** quando o evento tem `EventoFundamentacao` com `tipo_documento == OS`, usa `texto_fundamentacao`; senão mantém `oficio.motivo` |
| Demais campos | OK | cargo_chefia, data_extenso, destino, equipe_deslocamento, motivo, nome_chefia, ordem_de_servico, sede, unidade, email, endereco, unidade_rodape |

---

## 4. Fase 4 — Ajustes aplicados

1. **eventos/services/documentos/oficio.py**  
   - Inclusão de `'telefone': context['institucional'].get('telefone', '')` no mapping do template do ofício.

2. **eventos/services/documentos/justificativa.py**  
   - Inclusão de `'telefone': context['institucional'].get('telefone', '')` no mapping da justificativa.

3. **eventos/services/documentos/ordem_servico.py**  
   - Inclusão de `'telefone': context['institucional'].get('telefone', '')` no mapping da ordem de serviço.

4. **eventos/services/documentos/context.py**  
   - Função `_get_fundamentacao_texto_para_tipo(oficio, tipo_documento)` para obter `evento.fundamentacao.texto_fundamentacao` quando o evento tem fundamentação do tipo indicado (PT ou OS).  
   - Em `build_plano_trabalho_document_context`: uso de `_get_fundamentacao_texto_para_tipo(oficio, EventoFundamentacao.TIPO_PT)` para `plano_trabalho.objetivo`; fallback para `conteudo.motivo`.  
   - Em `build_ordem_servico_document_context`: uso de `_get_fundamentacao_texto_para_tipo(oficio, EventoFundamentacao.TIPO_OS)` para `ordem_servico.finalidade`; fallback para `conteudo.motivo`.  
   - Import de `EventoFundamentacao` em `context.py`.

5. **eventos/services/documentos/types.py**  
   - `PLANO_TRABALHO`: `implemented_formats` alterado de `(DocumentoFormato.DOCX,)` para `(DocumentoFormato.DOCX, DocumentoFormato.PDF)`.

6. **eventos/tests/test_eventos.py**  
   - Novo teste `test_download_pdf_do_plano_trabalho_quando_apto` para garantir download PDF do plano de trabalho quando o backend está disponível (com mock de `convert_docx_bytes_to_pdf_bytes`).

---

## 5. Fase 5 — DOCX e PDF

- **DOCX:** Continua funcional para os 5 documentos; backends e fluxo inalterados.  
- **PDF:** Ofício, Justificativa, Termo e Ordem de Serviço já tinham PDF; Plano de Trabalho passou a oferecer PDF quando o ambiente tem Windows + docx2pdf + pywin32 + Word.  
- A checagem técnica existente foi preservada; DOCX não depende de PDF.  
- Se o PDF estiver indisponível (ex.: ambiente não-Windows), apenas o botão/status de PDF fica indisponível; DOCX segue disponível.

---

## 6. Resumo das alterações (arquivos)

| Arquivo | Alteração |
|---------|-----------|
| eventos/services/documentos/oficio.py | Inclusão de `telefone` no mapping do template |
| eventos/services/documentos/justificativa.py | Inclusão de `telefone` no mapping |
| eventos/services/documentos/ordem_servico.py | Inclusão de `telefone` no mapping |
| eventos/services/documentos/context.py | `_get_fundamentacao_texto_para_tipo`; PT e OS usam fundamentação do evento quando existir |
| eventos/services/documentos/types.py | PLANO_TRABALHO com PDF em `implemented_formats` |
| eventos/tests/test_eventos.py | Teste `test_download_pdf_do_plano_trabalho_quando_apto` |
| RELATORIO_AUDITORIA_DOCUMENTAL.md | Criado (este relatório) |

---

## 7. Testes executados

- `python manage.py check` — OK (0 issues).  
- Testes do módulo eventos relacionados a ofício/documentos: classe `OficioDocumentosTest` — 38 testes (incluindo contexto documental, download DOCX/PDF por tipo, bloqueios por ofício incompleto, backends).  
- Novo teste de PDF para Plano de Trabalho incluído na mesma classe.

---

## 8. Resultado final por documento

| Documento | DOCX | PDF | Aderência ao modelo |
|------------|------|-----|----------------------|
| Ofício | funcional | funcional (quando ambiente permite) | alta |
| Justificativa | funcional | funcional (quando ambiente permite) | alta |
| Termo de autorização | funcional | funcional (quando ambiente permite) | alta |
| Plano de trabalho | funcional | funcional (quando ambiente permite) | alta |
| Ordem de serviço | funcional | funcional (quando ambiente permite) | alta |

---

## 9. Pendências reais

1. **Plano de trabalho:** Não existe modelo .docx oficial no repositório; continua sendo gerado por código. Se no futuro for fornecido um .docx de PT, será necessário mapear placeholders e passar a usar `render_docx_template_bytes` em vez de `create_base_document` + helpers.  
2. **Auditoria visual:** Recomenda-se conferir, em ambiente real, uma amostra de cada documento gerado (DOCX e PDF) contra os modelos oficiais (layout, quebras de linha, assinaturas).  
3. **Telefone:** O preenchimento de `telefone` depende de `ConfiguracaoSistema` ter o campo (ou `telefone_formatado`) preenchido; não foi criada migration — o campo já existe no contexto institucional.  
4. **Observações PT/OS:** O modelo `EventoFundamentacao` tem `observacoes_pt_os`; não foi solicitada inclusão nos documentos PT/OS nesta fase; pode ser feita em etapa futura se necessário.
