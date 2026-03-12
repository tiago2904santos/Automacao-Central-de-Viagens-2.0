# 1. Visão geral do módulo

O módulo atual de ofícios de viagem está concentrado principalmente no app `eventos`, com suporte de `cadastros`, `core` e dois services locais (`diarias` e `estimativa_local`).

Hoje ele funciona como um wizard de 4 steps:

1. `Step 1`: dados gerais do ofício, protocolo, motivo, custeio e viajantes.
2. `Step 2`: transporte, veículo e motorista.
3. `Step 3`: sede, destinos, trechos, retorno e cálculo de diárias.
4. `Step 4`: resumo e finalização.

Objetivo do módulo no projeto atual:

- criar e manter o cadastro operacional do ofício de viagem;
- vincular o ofício a um evento quando ele nasce pelo fluxo guiado;
- registrar quem viaja, como viaja, qual é o roteiro e qual é a estimativa de diárias;
- marcar o ofício como `RASCUNHO` ou `FINALIZADO`.

Como ele se encaixa no sistema:

- no fluxo guiado do evento, ele aparece na `Etapa 3`, depois da Etapa 1 do evento e da Etapa 2 de roteiros;
- o painel guiado do evento (`eventos.views.guiado_painel`) mostra a etapa `Ofícios do evento`;
- ao entrar na Etapa 3 do evento, o usuário vê a lista dos ofícios vinculados ao evento e pode criar um novo ofício ou editar/excluir um já existente.

Nível do fluxo:

- no nível do evento: existe um hub/lista de ofícios em `eventos.views.guiado_etapa_3`;
- no nível do ofício: o trabalho real acontece nas views `oficio_step1`, `oficio_step2`, `oficio_step3` e `oficio_step4`;
- o model `Oficio` aceita `evento=None`, então o objeto suporta existência fora de um evento, mas o fluxo de criação exposto hoje na UI nasce dentro do evento, pela URL `eventos:guiado-etapa-3-criar-oficio`.

Limite atual do módulo:

- não existe central de documentos funcional para o ofício no projeto atual;
- não há geração atual de arquivo de ofício, justificativa, plano de trabalho, ordem de serviço ou termos;
- o fluxo para em resumo/finalização do cadastro.

Observação importante de leitura do código:

- `eventos/views.py` contém duplicidade de helpers e views de `Step 3` e `Step 4`;
- em Python, a última definição do mesmo nome é a que fica ativa;
- este relatório descreve o comportamento efetivamente ativo, isto é, o das últimas definições do arquivo.

# 2. Arquivos envolvidos

## Models

| Arquivo | Função no módulo |
| --- | --- |
| `eventos/models.py` | Núcleo do módulo: `Oficio`, `OficioTrecho`, `ModeloMotivoViagem`, `Evento`, `EventoDestino`, `RoteiroEvento`, `RoteiroEventoDestino`, `RoteiroEventoTrecho`. |
| `cadastros/models.py` | Dependências operacionais: `Estado`, `Cidade`, `Viajante`, `Veiculo`, `CombustivelVeiculo`, `ConfiguracaoSistema`, `AssinaturaConfiguracao`, `Cargo`, `UnidadeLotacao`. |
| `documentos/models.py` | Hoje é apenas placeholder; não há model de documento gerado. |

## Views

| Arquivo | Função no módulo |
| --- | --- |
| `eventos/views.py` | Quase toda a lógica do módulo: hub da Etapa 3 do evento, CRUD de modelos de motivo, wizard Step 1-4, APIs de viajantes/motoristas/veículos, integração com roteiros do evento, cálculo de trechos e diárias. |
| `cadastros/views/viajantes.py` | Cadastro/edição de viajantes com retorno para o Step 1 ou Step 2 via parâmetro `next`; também salva rascunho para ir a cargos/unidades. |
| `cadastros/views/veiculos.py` | Cadastro/edição de veículos com retorno para o Step 2 via `next`; também salva rascunho para ir ao cadastro de combustíveis. |
| `cadastros/views/api.py` | API de cidades por estado usada no Step 3 e na Etapa 2 de roteiros. |
| `cadastros/views/configuracoes.py` | Mantém `ConfiguracaoSistema`, de onde sai a `cidade_sede_padrao` e as assinaturas por tipo documental. |
| `documentos/views.py` | Apenas placeholder geral do módulo `Documentos`; não integra com o fluxo de ofícios atual. |

## Forms

| Arquivo | Função no módulo |
| --- | --- |
| `eventos/forms.py` | `ModeloMotivoViagemForm`, `RoteiroEventoForm`, `OficioStep1Form`, `OficioStep2Form` e um `LegacyOficioStep2Form` não usado pela view ativa. |
| `cadastros/forms.py` | `ViajanteForm`, `VeiculoForm`, `ConfiguracaoSistemaForm` e formulários auxiliares consumidos indiretamente pelo módulo. |

## URLs

| Arquivo | Função no módulo |
| --- | --- |
| `config/urls.py` | Inclui os apps `cadastros` e `eventos` no projeto. |
| `eventos/urls.py` | Expõe o hub de ofícios do evento, o wizard Step 1-4, APIs auxiliares, rotas de roteiros do evento e modelos de motivo. |
| `cadastros/urls.py` | Expõe cadastro/edição de viajantes, veículos, combustíveis, cidades por estado e configurações do sistema. |
| `documentos/urls.py` | Apenas rota placeholder do app `documentos`; não existe rota funcional de documentos do ofício. |

## Templates

| Arquivo | Função no módulo |
| --- | --- |
| `templates/eventos/guiado/painel.html` | Painel do evento com cartões das etapas e marcação de `OK/Pendente/Em breve`. |
| `templates/eventos/guiado/etapa_3.html` | Lista/hub dos ofícios do evento. |
| `templates/eventos/oficio/_wizard_stepper.html` | Navegação visual dos 4 steps do wizard. |
| `templates/eventos/oficio/wizard_step1.html` | Tela do Step 1; contém HTML e JS do motivo, custeio e seleção de viajantes. |
| `templates/eventos/oficio/wizard_step2.html` | Tela do Step 2; contém HTML e JS de viatura, motorista e carona. |
| `templates/eventos/oficio/wizard_step3.html` | Tela do Step 3; contém HTML e JS de sede, destinos, trechos, retorno e diárias. |
| `templates/eventos/oficio/wizard_step4.html` | Tela do Step 4; resumo e ações finais. |
| `templates/eventos/oficio/excluir_confirm.html` | Confirma exclusão de ofício e informa reaproveitamento da lacuna na numeração. |
| `templates/eventos/oficio/documentos_placeholder.html` | Placeholder antigo de central de documentos; não está em uso pelo fluxo atual. |
| `templates/eventos/oficio/editar_placeholder.html` | Placeholder antigo de edição; não está em uso porque `oficio_editar` redireciona ao Step 1. |
| `templates/eventos/modelos_motivo/lista.html` | Lista de modelos de motivo, com retorno opcional ao Step 1. |
| `templates/eventos/modelos_motivo/form.html` | Cadastro/edição de modelo de motivo. |
| `templates/eventos/modelos_motivo/excluir_confirm.html` | Confirma exclusão de modelo de motivo. |
| `templates/eventos/guiado/etapa_2_lista.html` | Lista de roteiros do evento; fonte potencial do Step 3 do ofício. |
| `templates/eventos/guiado/roteiro_form.html` | Cadastro/edição de roteiro do evento; origem dos roteiros reutilizados pelo ofício. |
| `templates/cadastros/viajantes/form.html` | Cadastro/edição de viajante com retorno ao wizard e botões para gerenciar cargo/unidade. |
| `templates/cadastros/veiculos/form.html` | Cadastro/edição de veículo com retorno ao wizard e botão para gerenciar combustíveis. |
| `templates/cadastros/_aviso_rascunho.html` | Banner que avisa que viajante/veículo em rascunho não pode ser usado em outros módulos. |
| `templates/cadastros/configuracao_form.html` | Tela de configuração do sistema, de onde saem cidade sede padrão e assinaturas. |

## JS

| Arquivo | Função no módulo |
| --- | --- |
| `static/js/masks.js` | Máscaras de protocolo, placa, CPF, RG, telefone e CEP. |
| `templates/eventos/oficio/wizard_step1.html` | JS embutido para preview lateral, carregamento de modelo de motivo, autocomplete de viajantes e controle do campo de instituição de custeio. |
| `templates/eventos/oficio/wizard_step2.html` | JS embutido para busca exata/sugestão de veículo, seleção de motorista, modo manual e carona. |
| `templates/eventos/oficio/wizard_step3.html` | JS embutido para modo de roteiro, renderização dinâmica de destinos/trechos, estimativa local e cálculo assíncrono de diárias. |
| `templates/eventos/guiado/roteiro_form.html` | JS embutido para renderizar trechos do roteiro do evento e estimativa local na Etapa 2. |
| `templates/cadastros/viajantes/form.html` | JS embutido para RG/sem RG e normalização visual do cadastro do viajante. |
| `templates/cadastros/veiculos/form.html` | JS embutido para normalização visual do modelo do veículo. |

## Services / helpers

| Arquivo | Função no módulo |
| --- | --- |
| `eventos/utils.py` | Helpers de Step 2: busca de veículo finalizado, serialização para o ofício e mapeamento de tipo de viatura. |
| `eventos/services/diarias.py` | Regra de cálculo periodizado de diárias e inferência de `tipo_destino`. |
| `eventos/services/estimativa_local.py` | Estimativa local de km/tempo por coordenadas, sem API externa. |
| `core/utils/masks.py` | Normalização e formatação canônica de protocolo, placa e outros campos mascarados. |

## Testes

| Arquivo | Função no módulo |
| --- | --- |
| `eventos/tests/test_eventos.py` | Cobre hub da Etapa 3, wizard Step 1-4, protocolo, numeração, modelos de motivo, Step 2 de carona/manual, Step 3 com roteiros do evento e cálculo de diárias. |
| `cadastros/tests/test_cadastros.py` | Cobre retorno via `next` para Step 1/Step 2, uso apenas de cadastros finalizados e persistência de assinaturas/configurações relacionadas. |

## Outros

| Arquivo | Função no módulo |
| --- | --- |
| `eventos/migrations/0010_oficio_model.py` até `0017_oficio_quantidade_diarias_oficio_roteiro_evento_and_more.py` | Histórico da evolução do schema do ofício; não executam lógica em runtime, mas ajudam a entender a composição atual do model. |
| `documentos/views.py` e `documentos/urls.py` | Confirmam que o app de documentos ainda não oferece integração real com ofícios. |

Confirmações negativas:

- não encontrei `signals.py` relevante para ofícios no escopo atual;
- não encontrei `Manager` ou `QuerySet` customizado específico para o módulo;
- não há arquivo runtime de central de documentos do ofício além de placeholders não ligados às rotas atuais.

# 3. Modelagem de dados

## Observação geral

O módulo de ofícios usa models próprios em `eventos` e vários models de apoio em `cadastros`. Não há managers customizados, querysets customizados nem signals para esses models no código atual.

## `Oficio` (`eventos/models.py`)

Papel: model central do módulo.

### Campos de vínculo

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `evento` | `ForeignKey(Evento)` | `null=True`, `blank=True` | `on_delete=CASCADE`, `related_name='oficios'`. |
| `roteiro_evento` | `ForeignKey(RoteiroEvento)` | `null=True`, `blank=True` | `on_delete=SET_NULL`, `related_name='oficios'`. Guarda o roteiro do evento escolhido no Step 3 quando o modo é `EVENTO_EXISTENTE`. |
| `viajantes` | `ManyToManyField(cadastros.Viajante)` | `blank=True` | `related_name='oficios'`. |
| `veiculo` | `ForeignKey(cadastros.Veiculo)` | `null=True`, `blank=True` | `on_delete=SET_NULL`, `related_name='oficios'`. Guarda o vínculo com o cadastro finalizado quando encontrado por placa. |
| `motorista_viajante` | `ForeignKey(cadastros.Viajante)` | `null=True`, `blank=True` | `on_delete=SET_NULL`, `related_name='oficios_motorista'`. |
| `carona_oficio_referencia` | `ForeignKey(self)` | `null=True`, `blank=True` | `on_delete=SET_NULL`, `related_name='oficios_que_usam_carona'`. Campo existe, mas não é usado pela view ativa. |

### Campos do Step 1

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `numero` | `PositiveIntegerField` | `null=True`, `blank=True` | Indexado; preenchido automaticamente no `save()` na criação. |
| `ano` | `PositiveIntegerField` | `null=True`, `blank=True` | Indexado; associado à numeração anual. |
| `protocolo` | `CharField(max_length=80)` | `blank=True`, `default=''` | Banco aceita vazio, mas o `OficioStep1Form` exige preenchimento. |
| `data_criacao` | `DateField` | `null=True`, `blank=True` | Indexado; default lógico em `save()/clean()` é `timezone.localdate()`. |
| `modelo_motivo` | `ForeignKey(ModeloMotivoViagem)` | `null=True`, `blank=True` | `on_delete=SET_NULL`, `related_name='oficios'`. |
| `motivo` | `TextField` | `blank=True`, `default=''` | Texto livre. |
| `custeio_tipo` | `CharField(max_length=30)` | `blank=True`, `default='UNIDADE'` | Choices: `UNIDADE`, `OUTRA_INSTITUICAO`, `ONUS_LIMITADOS`. |
| `nome_instituicao_custeio` | `CharField(max_length=200)` | `blank=True`, `default=''` | Só faz sentido com `OUTRA_INSTITUICAO`. |
| `tipo_destino` | `CharField(max_length=20)` | `blank=True`, `default=''` | Choices: `INTERIOR`, `CAPITAL`, `BRASILIA`; preenchido pelo Step 3. |
| `roteiro_modo` | `CharField(max_length=20)` | `blank=True`, `default='ROTEIRO_PROPRIO'` | Choices: `EVENTO_EXISTENTE`, `ROTEIRO_PROPRIO`. |
| `estado_sede` | `ForeignKey(Estado)` | `null=True`, `blank=True` | `related_name='oficios_sede'`, `on_delete=SET_NULL`. |
| `cidade_sede` | `ForeignKey(Cidade)` | `null=True`, `blank=True` | `related_name='oficios_sede'`, `on_delete=SET_NULL`. |

### Campos do Step 2 e do retorno/diárias

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `placa` | `CharField(max_length=10)` | `blank=True`, `default=''` | Banco aceita vazio, mas `OficioStep2Form` exige. |
| `modelo` | `CharField(max_length=120)` | `blank=True`, `default=''` | Cópia textual do veículo. |
| `combustivel` | `CharField(max_length=80)` | `blank=True`, `default=''` | Cópia textual; não é FK. |
| `tipo_viatura` | `CharField(max_length=20)` | `blank=True`, `default='DESCARACTERIZADA'` | Choices: `CARACTERIZADA`, `DESCARACTERIZADA`. |
| `porte_transporte_armas` | `BooleanField` | `default=True` | Step 2 trata como `Sim/Não`. |
| `motorista` | `CharField(max_length=120)` | `blank=True`, `default=''` | Texto final do nome do motorista. |
| `motorista_carona` | `BooleanField` | `default=False` | Calculado no Step 2. |
| `motorista_oficio` | `CharField(max_length=80)` | `blank=True`, `default=''` | String `numero/ano` quando carona. |
| `motorista_oficio_numero` | `PositiveIntegerField` | `null=True`, `blank=True` | Obrigatório na UI quando carona. |
| `motorista_oficio_ano` | `PositiveIntegerField` | `null=True`, `blank=True` | Step 2 preenche com o ano corrente quando carona. |
| `motorista_protocolo` | `CharField(max_length=80)` | `blank=True`, `default=''` | Obrigatório na UI quando carona. |
| `retorno_saida_cidade` | `CharField(max_length=120)` | `blank=True`, `default=''` | Preenchido pelo Step 3 com a última cidade do roteiro. |
| `retorno_saida_data` | `DateField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `retorno_saida_hora` | `TimeField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `retorno_chegada_cidade` | `CharField(max_length=120)` | `blank=True`, `default=''` | Preenchido pelo Step 3 com a sede. |
| `retorno_chegada_data` | `DateField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `retorno_chegada_hora` | `TimeField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `quantidade_diarias` | `CharField(max_length=120)` | `blank=True`, `default=''` | Ex.: `1 x 100%`; salvo como texto. |
| `valor_diarias` | `CharField(max_length=80)` | `blank=True`, `default=''` | Ex.: `290,55`; salvo como texto. |
| `valor_diarias_extenso` | `TextField` | `blank=True`, `default=''` | Valor por extenso. |

### Campos gerais

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `status` | `CharField(max_length=20)` | `default='RASCUNHO'` | Choices: `RASCUNHO`, `FINALIZADO`; indexado. |
| `created_at` | `DateTimeField(auto_now_add=True)` | automático | Timestamp de criação. |
| `updated_at` | `DateTimeField(auto_now=True)` | automático | Timestamp de atualização. |

### Choices e regras relevantes

- `STATUS_CHOICES`: `RASCUNHO`, `FINALIZADO`.
- `CUSTEIO_CHOICES`: `UNIDADE`, `OUTRA_INSTITUICAO`, `ONUS_LIMITADOS`.
- `TIPO_DESTINO_CHOICES`: `INTERIOR`, `CAPITAL`, `BRASILIA`.
- `TIPO_VIATURA_CHOICES`: `CARACTERIZADA`, `DESCARACTERIZADA`.
- `ROTEIRO_MODO_CHOICES`: `EVENTO_EXISTENTE`, `ROTEIRO_PROPRIO`.

### Constraints

- `UniqueConstraint(fields=['ano', 'numero'], name='eventos_oficio_numero_ano_unique')`.

### Métodos, properties, `clean()` e `save()`

- `numero_formatado`: exibe `NN/AAAA`, com zero à esquerda no número; se faltar dado, retorna `EMPTY_MASK_DISPLAY`.
- `normalize_protocolo` e `format_protocolo`: encapsulam as regras de máscara de protocolo.
- `protocolo_formatado`: versão visual do protocolo salvo.
- `motorista_protocolo_formatado`: mesma lógica para o protocolo do motorista.
- `placa_formatada`: mesma lógica para a placa.
- `data_criacao_formatada_br`: exibe `dd/mm/aaaa`.
- `get_next_available_numero(ano)`: usa `select_for_update()` e devolve a menor lacuna livre daquele ano.
- `clean()`:
  - normaliza protocolo;
  - exige 9 dígitos se protocolo estiver preenchido;
  - define `data_criacao` se estiver vazia;
  - se houver `numero` sem `ano`, usa o ano de `data_criacao`;
  - limpa `nome_instituicao_custeio` quando o tipo não é `OUTRA_INSTITUICAO`;
  - exige `nome_instituicao_custeio` quando o tipo é `OUTRA_INSTITUICAO`.
- `save()`:
  - repete a normalização do protocolo;
  - define `data_criacao` quando vazia;
  - completa `ano` se já houver `numero`;
  - limpa `nome_instituicao_custeio` quando o custeio não é `OUTRA_INSTITUICAO`;
  - na criação (`self.pk is None`) e sem número, gera a numeração anual pela menor lacuna disponível;
  - faz retry de até 5 tentativas em caso de `IntegrityError` de concorrência.

Observação importante:

- no fluxo atual, o ofício já nasce numerado porque `guiado_etapa_3_criar_oficio()` chama `Oficio.objects.create(...)`, o que aciona esse `save()` customizado imediatamente.

## `ModeloMotivoViagem` (`eventos/models.py`)

Papel: modelo reutilizável de texto para o campo `motivo`.

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `codigo` | `CharField(max_length=80)` | obrigatório | Único; não é exposto no CRUD atual. |
| `nome` | `CharField(max_length=200)` | obrigatório | Nome amigável exibido na UI. |
| `texto` | `TextField` | obrigatório | Conteúdo do motivo. |
| `ordem` | `PositiveIntegerField` | `default=0` | Existe no model, mas a UI atual não usa para ordenar a lista. |
| `ativo` | `BooleanField` | `default=True` | Existe no model, mas o `save()` força `True`. |
| `padrao` | `BooleanField` | `default=False` | Um modelo pode ser marcado como padrão. |
| `created_at` | `DateTimeField(auto_now_add=True)` | automático | Timestamp. |
| `updated_at` | `DateTimeField(auto_now=True)` | automático | Timestamp. |

Meta:

- `ordering = ['nome']`.

Métodos:

- `build_unique_codigo(nome, exclude_pk=None)`:
  - slugifica o nome;
  - troca `-` por `_`;
  - limita a 80 caracteres;
  - gera sufixos `_2`, `_3`, etc. se necessário.
- `save()`:
  - normaliza `codigo` para minúsculo;
  - faz strip em `nome`;
  - força `ativo=True`;
  - gera `codigo` se estiver vazio;
  - se `padrao=True`, zera `padrao` dos demais.

Não há `clean()` customizado.

## `OficioTrecho` (`eventos/models.py`)

Papel: persistir os trechos de ida do ofício. O retorno fica separado em campos no próprio `Oficio`.

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `oficio` | `ForeignKey(Oficio)` | obrigatório | `on_delete=CASCADE`, `related_name='trechos'`. |
| `ordem` | `PositiveIntegerField` | `default=0` | Ordem sequencial do trecho. |
| `origem_estado` | `ForeignKey(Estado)` | `null=True`, `blank=True` | `on_delete=SET_NULL`. |
| `origem_cidade` | `ForeignKey(Cidade)` | `null=True`, `blank=True` | `on_delete=SET_NULL`. |
| `destino_estado` | `ForeignKey(Estado)` | `null=True`, `blank=True` | `on_delete=SET_NULL`. |
| `destino_cidade` | `ForeignKey(Cidade)` | `null=True`, `blank=True` | `on_delete=SET_NULL`. |
| `saida_data` | `DateField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `saida_hora` | `TimeField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `chegada_data` | `DateField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `chegada_hora` | `TimeField` | `null=True`, `blank=True` | Persistido no Step 3. |
| `distancia_km` | `DecimalField(max_digits=8, decimal_places=2)` | `null=True`, `blank=True` | Pode vir da estimativa local. |
| `duracao_estimada_min` | `PositiveIntegerField` | `null=True`, `blank=True` | Total de minutos. |
| `tempo_cru_estimado_min` | `PositiveIntegerField` | `null=True`, `blank=True` | Tempo base calculado. |
| `tempo_adicional_min` | `IntegerField` | `null=True`, `blank=True`, `default=0` | Folga ajustável. |
| `rota_fonte` | `CharField(max_length=30)` | `blank=True`, `default=''` | Ex.: `ESTIMATIVA_LOCAL`. |
| `rota_calculada_em` | `DateTimeField` | `null=True`, `blank=True` | Carimbado quando há estimativa. |
| `created_at` | `DateTimeField(auto_now_add=True)` | automático | Timestamp. |
| `updated_at` | `DateTimeField(auto_now=True)` | automático | Timestamp. |

Constraint:

- `UniqueConstraint(fields=['oficio', 'ordem'], name='eventos_oficiotrecho_oficio_ordem_unique')`.

Property:

- `tempo_total_final_min`: usa `tempo_cru_estimado_min + tempo_adicional_min` se houver, senão cai para `duracao_estimada_min`.

Não há `clean()` nem `save()` customizados.

## `Evento` (`eventos/models.py`)

Papel no módulo: contêiner do fluxo guiado. O ofício atual nasce dentro da Etapa 3 de um evento.

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `titulo` | `CharField(max_length=200)` | `blank=True` | Exibido no painel e no hub da Etapa 3. |
| `tipo_demanda` | `CharField(max_length=30)` | `blank=True`, `null=True` | Campo legado; não é usado diretamente pelo ofício. |
| `tipos_demanda` | `ManyToManyField(TipoDemandaEvento)` | `blank=True` | Não é consumido diretamente pelo wizard de ofício. |
| `descricao` | `TextField` | `blank=True` | Não é usada no wizard de ofício. |
| `data_inicio` | `DateField` | obrigatório | Exibida no painel do evento. |
| `data_fim` | `DateField` | obrigatório | Exibida no painel do evento. |
| `data_unica` | `BooleanField` | `default=False` | Apoia a geração do título. |
| `estado_principal` | `ForeignKey(Estado)` | `null=True`, `blank=True` | Pode servir como fallback de sede no Step 3. |
| `cidade_principal` | `ForeignKey(Cidade)` | `null=True`, `blank=True` | Pode servir como fallback de sede no Step 3. |
| `cidade_base` | `ForeignKey(Cidade)` | `null=True`, `blank=True` | Prioridade maior para pré-preencher a sede do Step 3. |
| `tem_convite_ou_oficio_evento` | `BooleanField` | `default=False` | Sem uso direto no wizard de ofício. |
| `status` | `CharField(max_length=20)` | `default='RASCUNHO'` | Status geral do evento. |
| `veiculo` | `ForeignKey(cadastros.Veiculo)` | `null=True`, `blank=True` | Composição operacional do evento; não é reaproveitado automaticamente pelo ofício. |
| `motorista` | `ForeignKey(cadastros.Viajante)` | `null=True`, `blank=True` | Composição operacional do evento; não é reaproveitado automaticamente pelo ofício. |
| `observacoes_operacionais` | `TextField` | `blank=True`, `default=''` | Não é puxado para o ofício. |
| `created_at` | `DateTimeField(auto_now_add=True)` | automático | Timestamp. |
| `updated_at` | `DateTimeField(auto_now=True)` | automático | Timestamp. |

Métodos relevantes:

- `gerar_titulo()`: monta título com tipos, destinos e datas.
- `montar_descricao_padrao()`: concatena descrições padrão dos tipos de demanda ativos.

Sem `clean()` customizado no trecho lido.

## `EventoDestino` (`eventos/models.py`)

Papel: destinos cadastrados na Etapa 1 do evento. O Step 3 do ofício os usa como pré-preenchimento quando não há roteiro do evento.

Campos:

- `evento`: `ForeignKey(Evento)`, obrigatório.
- `estado`: `ForeignKey(Estado)`, obrigatório, `on_delete=PROTECT`.
- `cidade`: `ForeignKey(Cidade)`, obrigatório, `on_delete=PROTECT`.
- `ordem`: `PositiveIntegerField(default=0)`.
- `created_at`, `updated_at`.

Sem `clean()`/`save()` customizados.

## `RoteiroEvento` (`eventos/models.py`)

Papel: roteiro cadastrado na Etapa 2 do evento e opcionalmente reutilizado no Step 3 do ofício.

| Campo | Tipo | Obrigatoriedade / default | Observações |
| --- | --- | --- | --- |
| `evento` | `ForeignKey(Evento)` | obrigatório | `related_name='roteiros'`. |
| `origem_estado` | `ForeignKey(Estado)` | `null=True`, `blank=True` | Sede do roteiro. |
| `origem_cidade` | `ForeignKey(Cidade)` | `null=True`, `blank=True` | Sede do roteiro. |
| `saida_dt` | `DateTimeField` | `null=True`, `blank=True` | Saída de ida. |
| `duracao_min` | `PositiveIntegerField` | `null=True`, `blank=True` | Campo legado; o cálculo atual relevante é por trecho. |
| `chegada_dt` | `DateTimeField` | `null=True`, `blank=True` | Chegada de ida. |
| `retorno_saida_dt` | `DateTimeField` | `null=True`, `blank=True` | Saída do retorno. |
| `retorno_duracao_min` | `PositiveIntegerField` | `null=True`, `blank=True` | Campo legado. |
| `retorno_chegada_dt` | `DateTimeField` | `null=True`, `blank=True` | Chegada do retorno. |
| `observacoes` | `TextField` | `blank=True`, `default=''` | `save()` coloca em maiúsculas. |
| `status` | `CharField(max_length=20)` | `default='RASCUNHO'` | Choices: `RASCUNHO`, `FINALIZADO`. |
| `created_at`, `updated_at` | `DateTimeField` | automático | Timestamps. |

Métodos e regras:

- `esta_completo()` exige:
  - `pk`;
  - `evento`;
  - sede (`origem_estado` e `origem_cidade`);
  - ao menos um destino;
  - `saida_dt`;
  - `chegada_dt`.
- `save()`:
  - uppercases `observacoes`;
  - se `duracao_min` estiver preenchida, recalcula `chegada_dt`;
  - se `retorno_saida_dt` e `duracao_min` estiverem preenchidos, recalcula `retorno_chegada_dt`;
  - define `status` como `FINALIZADO` ou `RASCUNHO` conforme `esta_completo()`.

## `RoteiroEventoDestino` (`eventos/models.py`)

Papel: destinos sequenciados do roteiro do evento.

Campos:

- `roteiro`: `ForeignKey(RoteiroEvento)`.
- `estado`: `ForeignKey(Estado)`.
- `cidade`: `ForeignKey(Cidade)`.
- `ordem`: `PositiveIntegerField(default=0)`.
- `created_at`, `updated_at`.

Sem `clean()`/`save()` customizados.

## `RoteiroEventoTrecho` (`eventos/models.py`)

Papel: trechos do roteiro do evento, usados como fonte para o ofício quando o Step 3 está em modo `EVENTO_EXISTENTE`.

Campos principais:

- `roteiro`: `ForeignKey(RoteiroEvento)`.
- `ordem`: `PositiveIntegerField(default=0)`.
- `tipo`: `CharField(max_length=10)`, choices `IDA` e `RETORNO`.
- `origem_estado`, `origem_cidade`, `destino_estado`, `destino_cidade`: FKs opcionais.
- `saida_dt`, `chegada_dt`: `DateTimeField`.
- `distancia_km`: `DecimalField(8,2)`.
- `duracao_estimada_min`: `PositiveIntegerField`.
- `tempo_cru_estimado_min`: `PositiveIntegerField`.
- `tempo_adicional_min`: `IntegerField(default=0)`.
- `rota_fonte`: `CharField(max_length=30, default='')`.
- `rota_calculada_em`: `DateTimeField`.
- `created_at`, `updated_at`.

Property:

- `tempo_total_final_min`: soma `tempo_cru_estimado_min + tempo_adicional_min`, com fallback para `duracao_estimada_min`.

Sem `clean()` customizado; `save()` customizado não existe nesse model.

## `Viajante` (`cadastros/models.py`)

Papel: origem dos viajantes do Step 1 e também dos motoristas do Step 2.

Campos:

- `nome`: `CharField(max_length=160, blank=True, default='')`.
- `status`: `CharField(max_length=20)`, choices `RASCUNHO` e `FINALIZADO`.
- `cargo`: `ForeignKey(Cargo)`, opcional.
- `rg`: `CharField(max_length=30, blank=True, default='')`.
- `sem_rg`: `BooleanField(default=False)`.
- `cpf`: `CharField(max_length=14, blank=True, default='')`.
- `telefone`: `CharField(max_length=20, blank=True, default='')`.
- `unidade_lotacao`: `ForeignKey(UnidadeLotacao)`, opcional.
- `created_at`, `updated_at`.

Constraints:

- unicidade de `nome` quando preenchido;
- unicidade de `cpf` quando preenchido;
- unicidade de `rg` quando preenchido e diferente de `NAO POSSUI RG`;
- unicidade de `telefone` quando preenchido.

Métodos/properties:

- `rg_formatado`, `cpf_formatado`, `telefone_formatado`.
- `esta_completo()` exige nome, cargo, CPF válido com 11 dígitos, telefone com 10 ou 11 dígitos, unidade de lotação e RG preenchido ou `sem_rg=True`.
- `save()` coloca `nome` em maiúsculas e, se `sem_rg=True`, grava `RG_NAO_POSSUI_CANONICAL`.

Observação:

- as APIs do Step 1 e do Step 2 só buscam viajantes `FINALIZADO`.

## `Veiculo` (`cadastros/models.py`)

Papel: origem opcional do veículo do Step 2.

Campos:

- `placa`: `CharField(max_length=10, blank=True, default='')`.
- `modelo`: `CharField(max_length=120, blank=True, default='')`.
- `combustivel`: `ForeignKey(CombustivelVeiculo)`, opcional.
- `tipo`: `CharField(max_length=20)`, choices `CARACTERIZADO` e `DESCARACTERIZADO`.
- `status`: `CharField(max_length=20)`, choices `RASCUNHO` e `FINALIZADO`.
- `created_at`, `updated_at`.

Constraint:

- unicidade de `placa` quando preenchida.

Métodos/properties:

- `placa_formatada`.
- `_placa_valida()` aceita padrão antigo ou Mercosul com 7 caracteres.
- `esta_completo()` exige placa válida, modelo, combustível e tipo válido.
- `save()` normaliza placa e uppercases modelo.

Observação:

- o ofício guarda o `veiculo_id` quando encontra um veículo finalizado, mas também copia placa/modelo/combustível em campos textuais próprios.

## `CombustivelVeiculo` (`cadastros/models.py`)

Papel: base de combustível usada no cadastro do veículo e como datalist no Step 2.

Campos:

- `nome`: `CharField(max_length=60, unique=True)`.
- `is_padrao`: `BooleanField(default=False)`.
- `created_at`, `updated_at`.

Método:

- `save()` uppercases `nome` e, se `is_padrao=True`, remove o padrão dos demais.

## `Estado` e `Cidade` (`cadastros/models.py`)

Papel: base geográfica usada em evento, roteiro, Step 3 e estimativa local.

### `Estado`

- `codigo_ibge`: `CharField(max_length=10, unique=True, db_index=True, null=True, blank=True)`.
- `nome`: `CharField(max_length=100)`.
- `sigla`: `CharField(max_length=2, unique=True)`.
- `ativo`: `BooleanField(default=True)`.
- `created_at`, `updated_at`.

### `Cidade`

- `codigo_ibge`: `CharField(max_length=10, unique=True, db_index=True, null=True, blank=True)`.
- `nome`: `CharField(max_length=200)`.
- `estado`: `ForeignKey(Estado, on_delete=PROTECT, related_name='cidades')`.
- `latitude`: `DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)`.
- `longitude`: `DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)`.
- `ativo`: `BooleanField(default=True)`.
- `created_at`, `updated_at`.

Observação:

- `latitude` e `longitude` são indispensáveis para a estimativa local de km/tempo.

## `ConfiguracaoSistema` (`cadastros/models.py`)

Papel no módulo: fallback de sede padrão do Step 3 e armazenamento de assinaturas por tipo documental.

Campos relevantes:

- `cidade_sede_padrao`: `ForeignKey(Cidade)`, opcional.
- `prazo_justificativa_dias`: `PositiveIntegerField(default=10)`.
- `nome_orgao`, `sigla_orgao`, `divisao`, `unidade`.
- endereço: `cep`, `logradouro`, `bairro`, `cidade_endereco`, `uf`, `numero`.
- contato: `telefone`, `email`.
- `updated_at`.

Métodos/properties:

- `cep_formatado`, `telefone_formatado`.
- `get_singleton()`: retorna/cria o singleton `pk=1`.

Observação:

- o wizard de ofício usa `cidade_sede_padrao` apenas como fallback quando não consegue inferir a sede a partir do evento.

## `AssinaturaConfiguracao` (`cadastros/models.py`)

Papel: armazena assinaturas configuráveis para `OFICIO`, `JUSTIFICATIVA`, `PLANO_TRABALHO` e `ORDEM_SERVICO`.

Campos:

- `configuracao`: `ForeignKey(ConfiguracaoSistema)`.
- `tipo`: `CharField(max_length=20)`, choices `OFICIO`, `JUSTIFICATIVA`, `PLANO_TRABALHO`, `ORDEM_SERVICO`.
- `ordem`: `PositiveSmallIntegerField(default=1)`.
- `viajante`: `ForeignKey(Viajante)`, opcional.
- `ativo`: `BooleanField(default=True)`.
- `created_at`, `updated_at`.

Constraint:

- unicidade por `configuracao + tipo + ordem`.

Observação importante:

- a configuração existe e é salva pela tela de configurações;
- no fluxo atual de ofício, essas assinaturas ainda não são consumidas para gerar documento algum.

## `Cargo` e `UnidadeLotacao` (`cadastros/models.py`)

Papel indireto:

- `Cargo` aparece nas buscas e previews de viajantes/motoristas;
- `UnidadeLotacao` entra na regra de completude do viajante.

Campos:

- `Cargo`: `nome`, `is_padrao`, `created_at`, `updated_at`; `save()` uppercases e mantém só um padrão.
- `UnidadeLotacao`: `nome`, `created_at`, `updated_at`; `save()` uppercases.

## `EventoParticipante` (`eventos/models.py`)

Existe no app `eventos`, mas não é usado pelo wizard de ofício atual.

Campos:

- `evento`: `ForeignKey(Evento)`.
- `viajante`: `ForeignKey(cadastros.Viajante)`.
- `ordem`: `PositiveIntegerField(default=0)`.
- `created_at`.

Constraint:

- unicidade por `evento + viajante`.

Observação:

- o Step 1 usa `Oficio.viajantes`, não `EventoParticipante`.

## Modelos que não existem hoje

Não encontrei model atual para:

- documento gerado do ofício;
- upload/arquivo do ofício;
- justificativa vinculada ao ofício;
- termo vinculado ao ofício;
- plano de trabalho vinculado ao ofício;
- ordem de serviço vinculada ao ofício.

# 4. Fluxo completo do usuário

1. O usuário abre o painel guiado do evento em `eventos.views.guiado_painel`.
2. No painel, a Etapa 3 aparece como `Ofícios do evento`.
3. Ao entrar em `eventos.views.guiado_etapa_3`, o sistema lista os ofícios do evento por `ano`, `numero`, `id`.
4. Ao clicar em `Criar Ofício neste Evento`, a view `guiado_etapa_3_criar_oficio` cria imediatamente um `Oficio` com `evento=<evento>` e `status=RASCUNHO`, já numerado pelo `save()` do model, e redireciona para `eventos:oficio-step1`.
5. No `Step 1`, o usuário informa/confirma protocolo, motivo, custeio e escolhe viajantes.
6. Ainda no `Step 1`, ele pode abrir o gerenciador de modelos de motivo e voltar para o mesmo ofício, ou cadastrar um novo viajante e voltar para o mesmo Step 1 via `next`.
7. Ao avançar, o `Step 2` coleta dados de veículo e motorista.
8. No `Step 2`, o usuário pode localizar uma viatura finalizada por placa/modelo, preencher manualmente se a placa não existir no cadastro, escolher um motorista dentre os viajantes finalizados, usar motorista manual, preencher ofício/protocolo do motorista quando ele é carona e cadastrar nova viatura ou novo viajante com retorno ao mesmo Step 2.
9. Ao avançar, o `Step 3` trata do roteiro do ofício.
10. No `Step 3`, o usuário escolhe entre usar um `RoteiroEvento` já existente do evento ou criar um roteiro próprio do ofício.
11. O `Step 3` carrega a sede e os destinos de acordo com uma ordem de prioridade: trechos já salvos do próprio ofício, roteiro já vinculado, único roteiro do evento, seleção manual entre vários roteiros, destinos do evento ou fallback de configuração.
12. O usuário preenche datas/horas de ida e retorno, pode pedir estimativa local de km/tempo e pode acionar a calculadora de diárias.
13. Ao salvar o `Step 3`, o sistema persiste `OficioTrecho`, campos de retorno do `Oficio` e também `tipo_destino`, `quantidade_diarias`, `valor_diarias` e `valor_diarias_extenso`.
14. No `Step 4`, o usuário vê um resumo consolidado de tudo que foi salvo.
15. No `Step 4`, ele pode finalizar o ofício, excluir o ofício, voltar para a lista da Etapa 3 do evento ou voltar ao `Step 3`.

Comportamentos relevantes do fluxo atual:

- o ofício nasce no contexto do evento, mas os steps funcionam em URLs de `oficio/<pk>/...`;
- o stepper é clicável e não impõe bloqueio por ordem;
- um ofício finalizado continua editável porque as views dos Steps 1-3 não barram `status=FINALIZADO`;
- a lista da Etapa 3 considera a etapa “OK” se existir qualquer ofício vinculado ao evento, independentemente de estar finalizado ou não.

# 5. Etapas / Wizard

O wizard do ofício é implementado com 4 telas reais e um stepper comum em `templates/eventos/oficio/_wizard_stepper.html`.

## Estrutura de navegação

- `1. Dados e viajantes` -> `eventos:oficio-step1`
- `2. Transporte` -> `eventos:oficio-step2`
- `3. Trechos` -> `eventos:oficio-step3`
- `4. Resumo` -> `eventos:oficio-step4`

## Regras estruturais do wizard

- não existe `SessionWizardView`; o fluxo é manual, view por view;
- cada step salva diretamente no banco;
- a navegação entre steps é feita por `redirect` após POST válido;
- os steps podem ser reabertos quantas vezes o usuário quiser;
- as telas de `Step 1`, `Step 2` e `Step 3` mantêm um “relatório rápido”/preview lateral;
- o `Step 4` consolida o que já está persistido.

## Guardas e bloqueios

Não existem guardas rígidas de progressão como:

- “não pode abrir Step 2 sem Step 1”;
- “não pode abrir Step 4 se o Step 3 estiver vazio”;
- “não pode editar após finalização”.

O que existe são validações locais no POST de cada step.

# 6. Campos e comportamentos do Step 1

View ativa: `eventos.views.oficio_step1`  
Form ativo: `eventos.forms.OficioStep1Form`  
Template: `templates/eventos/oficio/wizard_step1.html`

## Campos exibidos

- `oficio_numero`: somente leitura; já vem numerado no fluxo atual.
- `protocolo`: obrigatório; usa máscara `data-mask="protocolo"`.
- `data_criacao`: somente leitura; exibição em `dd/mm/aaaa`.
- `modelo_motivo`: opcional; select de `ModeloMotivoViagem`.
- `motivo`: textarea livre.
- `custeio_tipo`: obrigatório.
- `nome_instituicao_custeio`: condicional.
- `viajantes`: tecnicamente é um `ModelMultipleChoiceField`, mas fica oculto (`MultipleHiddenInput`) e é manipulado por JS.

## Carga inicial

Na abertura do Step 1:

- `oficio_numero` recebe `oficio.numero_formatado`;
- `protocolo` recebe versão mascarada;
- `data_criacao` usa `oficio.data_criacao`; se não houver, usa `created_at.date()`; se ainda assim não houver, usa `timezone.localdate()`;
- `modelo_motivo` recebe o já salvo no ofício; se não houver, tenta o primeiro modelo com `padrao=True`;
- `motivo` recebe o texto salvo no ofício; se estiver vazio e houver modelo inicial, recebe `modelo.texto`;
- `custeio_tipo` cai em `UNIDADE` se o ofício estiver vazio;
- `viajantes` recebe os IDs já vinculados ao ofício.

## Busca e seleção de viajantes

API: `eventos.views.oficio_step1_viajantes_api`

Regras:

- só busca viajantes com `status=FINALIZADO`;
- pesquisa por `nome`, `rg` e `cpf`;
- limita a 20 resultados;
- retorna payload serializado com `id`, `nome`, `label`, `text`, `rg`, `cpf`, `cargo`.

Comportamento da UI:

- autocomplete com debounce;
- suporte a teclado (`ArrowUp`, `ArrowDown`, `Enter`, `Tab`, `Escape`);
- chips com remoção;
- hidden inputs `name="viajantes"` para persistir os IDs escolhidos;
- cards de preview lateral com RG, CPF e cargo.

## Modelos de motivo dentro do Step 1

O template oferece:

- link para gerenciar modelos existentes;
- carregamento do texto do modelo via API `eventos.views.modelo_motivo_texto_api`;
- ação de salvar o motivo atual como novo modelo.

Quando o usuário escolhe um modelo no select:

- o JS chama a API de texto;
- o conteúdo retornado substitui o textarea de motivo.

Quando o usuário escolhe “Salvar motivo atual como novo modelo”:

- o POST vai para a mesma view;
- se `motivo` estiver vazio, a view bloqueia e mostra mensagem;
- o nome do novo modelo pode vir de `novo_modelo_nome`;
- se não vier, a view usa `Modelo dd/mm/aaaa hh:mm`;
- cria `ModeloMotivoViagem(nome=..., texto=...)`;
- vincula o novo modelo ao ofício;
- redireciona de volta ao próprio Step 1.

## Custeio no Step 1

Comportamento do campo condicional:

- `nome_instituicao_custeio` fica desabilitado na UI quando o tipo não é `OUTRA_INSTITUICAO`;
- ao trocar para `OUTRA_INSTITUICAO`, o JS libera o campo;
- o preview lateral concatena tipo + nome da instituição quando aplicável.

## Validações do Step 1

`OficioStep1Form.clean_protocolo()`:

- normaliza o protocolo para dígitos;
- exige exatamente 9 dígitos;
- mensagem: `Informe o protocolo no formato XX.XXX.XXX-X.`

`OficioStep1Form.clean()`:

- exige ao menos um viajante;
- exige `nome_instituicao_custeio` quando `custeio_tipo=OUTRA_INSTITUICAO`;
- limpa `nome_instituicao_custeio` para os demais tipos;
- se há `modelo_motivo` e `motivo` vazio, injeta `modelo.texto`;
- se `data_criacao` vier vazia, usa `timezone.localdate()`.

## Persistência do Step 1

A view salva:

- `protocolo`
- `data_criacao`
- `modelo_motivo`
- `motivo`
- `custeio_tipo`
- `nome_instituicao_custeio`

Depois faz:

- `oficio.viajantes.set(...)`

Observação:

- o Step 1 não gera numeração; a numeração já foi gerada na criação do `Oficio`.

# 7. Campos e comportamentos do Step 2

View ativa: `eventos.views.oficio_step2`  
Form ativo: `eventos.forms.OficioStep2Form`  
Template: `templates/eventos/oficio/wizard_step2.html`

## Campos exibidos

- `placa`
- `modelo`
- `combustivel`
- `tipo_viatura`
- `porte_transporte_armas`
- `motorista_viajante` (hidden)
- `motorista_nome`
- `motorista_oficio_numero`
- `motorista_oficio_ano` (hidden)
- `motorista_protocolo`

## Lookup de veículo

APIs:

- `eventos.views.oficio_step2_veiculos_busca_api`
- `eventos.views.oficio_step2_veiculo_api`

Regras:

- trabalham só com veículos `FINALIZADO`;
- busca por placa ou modelo;
- a busca exata por placa devolve `found=true/false`;
- a busca de sugestões devolve payload com placa formatada, modelo, combustível e tipo de viatura.

Comportamento da UI:

- ao digitar uma placa completa, faz lookup exato com debounce;
- se encontrar, preenche `modelo`, `combustivel` e `tipo_viatura`;
- se não encontrar, mostra mensagem de que o preenchimento manual é permitido;
- também oferece lista de sugestões por placa/modelo;
- existe link para cadastrar nova viatura com retorno ao mesmo Step 2.

## Regras de preenchimento do veículo

No backend:

- `clean_placa()` normaliza a placa;
- `clean_modelo()` uppercases e normaliza espaços;
- `clean_combustivel()` uppercases e normaliza espaços;
- na `clean()` do form, se a placa bater em um veículo finalizado:
  - preenche `modelo` se vier vazio;
  - preenche `combustivel` se vier vazio;
  - preenche `tipo_viatura` se vier vazio, mapeando `Veiculo.tipo` via `eventos.utils.mapear_tipo_viatura_para_oficio`.

Campos obrigatórios na prática:

- `placa`
- `modelo`
- `combustivel`

Banco:

- o `Oficio` continua aceitando esses campos vazios, mas a UI não.

## Seleção de motorista

API: `eventos.views.oficio_step2_motoristas_api`

Regras:

- busca apenas viajantes `FINALIZADO`;
- pesquisa por nome, RG e CPF;
- payload igual ao usado para viajantes do Step 1.

Modos possíveis:

- motorista selecionado dentre viajantes finalizados;
- motorista manual (`__manual__`).

O form carrega um payload interno com:

- opção vazia;
- opção `Motorista sem cadastro`;
- todos os motoristas finalizados, marcando `(carona)` quando o servidor não está entre os viajantes do ofício.

## Regra de carona

`OficioStep2Form` considera `motorista_carona=True` quando:

- o motorista é manual; ou
- o motorista escolhido não está em `oficio.viajantes`.

Quando `motorista_carona=True`, tornam-se obrigatórios:

- `motorista_oficio_numero`
- `motorista_protocolo`

E o form monta:

- `motorista_oficio = f'{numero}/{ano}'`

Quando `motorista_carona=False`, o form limpa:

- `motorista_oficio_numero`
- `motorista_oficio_ano`
- `motorista_oficio`
- `motorista_protocolo`

## Persistência do Step 2

A view salva:

- `veiculo_id` quando o lookup encontrou um cadastro finalizado; caso contrário, `None`;
- `placa`, `modelo`, `combustivel`, `tipo_viatura`, `porte_transporte_armas`;
- `motorista_viajante_id` quando houver escolha de servidor;
- `motorista` com o nome final, mesmo quando existe `motorista_viajante`;
- `motorista_carona`;
- `motorista_oficio_numero`, `motorista_oficio_ano`, `motorista_oficio`, `motorista_protocolo`.

Resumo importante:

- o ofício guarda snapshot textual do veículo e do motorista;
- o vínculo com cadastro é opcional e adicional.

# 8. Campos e comportamentos do Step 3

View ativa: `eventos.views.oficio_step3`  
Template: `templates/eventos/oficio/wizard_step3.html`

## Blocos da tela

1. Fonte do roteiro.
2. Sede (`estado` e `cidade`).
3. Destinos dinâmicos.
4. Trechos de ida.
5. Retorno.
6. Calculadora de diárias.
7. Preview lateral.

## Modos de roteiro

Choices persistidos em `Oficio.roteiro_modo`:

- `EVENTO_EXISTENTE`
- `ROTEIRO_PROPRIO`

Quando o modo é `EVENTO_EXISTENTE`:

- o usuário deve escolher um `RoteiroEvento` do mesmo evento;
- a view valida se o roteiro pertence ao evento do ofício;
- os dados do roteiro são clonados para o estado do Step 3;
- editar o ofício não altera o roteiro original do evento.

Quando o modo é `ROTEIRO_PROPRIO`:

- a estrutura de destinos/trechos nasce do próprio formulário do ofício.

## Como o Step 3 decide o estado inicial

Helper ativo: `eventos.views._get_oficio_step3_seed_state`

Prioridade:

1. se houver `OficioTrecho` salvo, reabre exatamente o estado salvo do próprio ofício;
2. se o ofício já tiver `roteiro_evento_id`, reabre a partir desse roteiro;
3. se o evento tiver exatamente um roteiro, pré-carrega esse roteiro;
4. se houver vários roteiros do evento, abre em modo `EVENTO_EXISTENTE` vazio, pedindo que o usuário selecione um;
5. se não houver roteiro, mas houver destinos no evento, cria um roteiro próprio pré-preenchido com os destinos do evento;
6. caso contrário, cria estado vazio usando a sede do evento ou a `ConfiguracaoSistema.cidade_sede_padrao`.

## Destinos e trechos

Helper estrutural: `eventos.views._estrutura_trechos`

Regras:

- a estrutura sempre é `sede -> destino1 -> destino2 -> ... -> sede`;
- o retorno não vira `OficioTrecho`; ele fica em `state['retorno']` e depois em campos próprios do `Oficio`;
- `OficioTrecho` guarda apenas os trechos de ida/intermediários.

Cada trecho do estado do Step 3 carrega:

- ordem;
- nomes de origem e destino;
- IDs de origem/destino;
- `saida_data`, `saida_hora`;
- `chegada_data`, `chegada_hora`;
- `distancia_km`;
- `tempo_cru_estimado_min`;
- `tempo_adicional_min`;
- `duracao_estimada_min`;
- `rota_fonte`.

## Validações do Step 3

Helper ativo: `eventos.views._validate_step3_state`

Validações:

- se modo evento, o roteiro do evento é obrigatório;
- o roteiro selecionado deve pertencer ao evento do ofício;
- sede: `estado` obrigatório;
- sede: `cidade` obrigatória;
- a cidade da sede deve pertencer ao estado da sede;
- deve existir ao menos um destino;
- cada destino precisa apontar para cidade ativa pertencente ao estado ativo escolhido;
- cada trecho precisa de saída e chegada;
- chegada do trecho não pode ser anterior à saída;
- retorno precisa de saída e chegada;
- chegada do retorno não pode ser anterior à saída;
- `tempo_adicional_min` é convertido para inteiro e truncado para mínimo zero;
- `distancia_km` é parseada para `Decimal`;
- `duracao_estimada_min` é recomputada se necessário a partir de `tempo_cru + adicional`.

## Estimativa local de km/tempo

Endpoint usado pelo Step 3:

- `eventos.views.estimar_km_por_cidades`

Entrada:

- JSON com `origem_cidade_id` e `destino_cidade_id`.

Saída:

- `ok`
- `distancia_km`
- `duracao_estimada_min`
- `duracao_estimada_hhmm`
- `tempo_cru_estimado_min`
- `tempo_adicional_sugerido_min`
- `perfil_rota`
- `rota_fonte`
- `erro`

Regras do service `eventos/services/estimativa_local.py`:

- usa coordenadas de `Cidade.latitude` e `Cidade.longitude`;
- calcula distância em linha reta por Haversine;
- aplica fator rodoviário progressivo por faixa;
- aplica velocidade média progressiva com teto;
- arredonda o tempo cru para o múltiplo de 5 mais próximo;
- sugere tempo adicional de 15/30/45 minutos conforme perfil da rota;
- marca `rota_fonte = ESTIMATIVA_LOCAL`.

Persistência:

- no Step 3 do ofício, a estimativa não é salva imediatamente em endpoint dedicado;
- ela só vai para `OficioTrecho` quando o Step 3 é salvo.

## Diárias no Step 3

Endpoint:

- `eventos.views.oficio_step3_calcular_diarias`

Esse endpoint:

- reconstrói o estado do Step 3 a partir do POST;
- não chama `_validate_step3_state`;
- tenta calcular diárias com base nos trechos e no retorno;
- devolve `400` com erro se faltarem dados mínimos.

O cálculo real fica em `eventos/services/diarias.py`:

- classifica parada como `INTERIOR`, `CAPITAL` ou `BRASILIA`;
- usa tabela fixa de valores por tipo de destino;
- calcula períodos entre saídas e chegada final à sede;
- gera `total_diarias`, `total_horas`, `total_valor`, `valor_extenso`, métricas por servidor e `valor_unitario_referencia`;
- o número de servidores é `oficio.viajantes.count()`.

## Persistência do Step 3

Helper ativo: `eventos.views._salvar_step3_oficio`

Ao salvar:

- define `Oficio.roteiro_modo`;
- define `Oficio.roteiro_evento` quando o modo é evento; caso contrário, limpa;
- salva `estado_sede` e `cidade_sede`;
- calcula e salva `tipo_destino`;
- salva `retorno_saida_cidade`, `retorno_saida_data`, `retorno_saida_hora`;
- salva `retorno_chegada_cidade`, `retorno_chegada_data`, `retorno_chegada_hora`;
- salva `quantidade_diarias`, `valor_diarias`, `valor_diarias_extenso`;
- apaga todos os `OficioTrecho` anteriores;
- recria os `OficioTrecho` em `bulk_create`.

Isso significa:

- os IDs dos trechos do ofício não são estáveis entre uma edição e outra;
- o Step 3 sempre persiste por substituição total.

# 9. Campos e comportamentos do Step 4

View ativa: `eventos.views.oficio_step4`  
Template: `templates/eventos/oficio/wizard_step4.html`

## O que a tela exibe

Resumo de:

- número/ano;
- protocolo;
- motivo;
- custeio;
- viajantes;
- placa/modelo;
- combustível;
- porte/transporte de armas;
- motorista;
- protocolo do motorista;
- trechos do Step 3;
- diárias do Step 3;
- status.

Os dados vêm de:

- campos persistidos no `Oficio`;
- relacionamento `oficio.viajantes`;
- preview montado por `eventos.views._build_oficio_step3_preview`.

## Como o Step 4 carrega os trechos e diárias

Na abertura:

- tenta reconstruir o estado salvo do Step 3 com `_get_oficio_step3_saved_state`;
- tenta recalcular diárias a partir desse estado;
- se não conseguir, usa `_build_step3_diarias_fallback`, que lê `quantidade_diarias`, `valor_diarias` e `valor_diarias_extenso` salvos no `Oficio`.

## Ações do Step 4

POST possíveis:

- `finalizar=1`
- `voltar_etapa3=1`

Botões visíveis:

- `Finalizar ofício` quando ainda não está finalizado;
- `Excluir ofício`;
- `Voltar para Ofícios do evento` quando há evento;
- `Voltar (Step 3)`.

## Finalização

Quando o usuário clica em finalizar:

- a view apenas faz `oficio.status = FINALIZADO`;
- salva `status` e `updated_at`;
- não revalida Step 1, Step 2 nem Step 3;
- não bloqueia inconsistências remanescentes;
- não gera documento algum.

# 10. Numeração do ofício

A numeração atual do ofício é responsabilidade do próprio model `Oficio`, em `eventos/models.py`.

## Quando a numeração acontece

Ela acontece na criação do objeto, não no Step 1.

Fluxo real:

- `guiado_etapa_3_criar_oficio()` chama `Oficio.objects.create(evento=evento, status=RASCUNHO)`;
- o `save()` do model detecta `creating=True` e `numero` vazio;
- define `data_criacao` se necessário;
- define `ano` a partir de `self.ano` ou do ano de `data_criacao`;
- chama `get_next_available_numero(ano)`;
- grava o objeto já com `numero` e `ano`.

## Algoritmo

`get_next_available_numero(ano)`:

- filtra ofícios do mesmo ano;
- ignora `numero=None`;
- ordena por `numero`;
- usa `select_for_update()` para concorrência;
- percorre os números usados;
- devolve a menor lacuna livre.

Exemplo implícito do algoritmo:

- se existem `1, 2, 3, 5`, o próximo é `4`;
- se existem `1, 2, 3`, o próximo é `4`;
- se não existe nenhum, o próximo é `1`.

## Garantia de integridade

Há duas camadas:

- `UniqueConstraint(fields=['ano', 'numero'])`;
- retry no `save()` em caso de `IntegrityError`, até 5 tentativas.

## Reutilização de lacuna

Quando um ofício é excluído:

- o número fica livre novamente;
- a própria tela `templates/eventos/oficio/excluir_confirm.html` informa isso;
- a próxima criação no mesmo ano reaproveita a lacuna.

## Exibição

- `numero_formatado` exibe `NN/AAAA`;
- na lista da Etapa 3 e no Step 4, essa é a forma exibida;
- com número `1` e ano `2026`, a visualização é `01/2026`.

# 11. Protocolo

## Campo do ofício

- model: `Oficio.protocolo`;
- form: `OficioStep1Form.protocolo`;
- máscara visual: `static/js/masks.js`;
- normalização/formatação canônica: `core/utils/masks.py`.

## Formato e máscara

Formato visual:

- `XX.XXX.XXX-X`

Formato persistido:

- somente 9 dígitos, sem pontuação.

Exemplo:

- usuário digita `12.345.678-9`;
- o form normaliza para `123456789`;
- o banco guarda `123456789`;
- a reabertura do step exibe novamente `12.345.678-9`.

## Validação

Step 1:

- obrigatório na UI;
- `clean_protocolo()` exige exatamente 9 dígitos após normalização.

Model:

- `Oficio.clean()` e `Oficio.save()` também validam 9 dígitos se houver valor.

Observação:

- o banco aceita `blank=True`, mas a UI atual do Step 1 não.

## Reexibição

Reexibição mascarada ocorre em:

- `Step 1`;
- lista da Etapa 3 do evento;
- `Step 4`.

## Protocolo do motorista

Campo:

- `Oficio.motorista_protocolo`

Regras:

- opcional quando o motorista não é carona;
- obrigatório quando `motorista_carona=True`;
- também é normalizado para 9 dígitos;
- também é reexibido com máscara (`motorista_protocolo_formatado`).

# 12. Modelos de motivo

## Cadastro

Views:

- `modelos_motivo_lista`
- `modelos_motivo_cadastrar`
- `modelos_motivo_editar`
- `modelos_motivo_excluir`
- `modelos_motivo_definir_padrao`
- `modelo_motivo_texto_api`

Form:

- `ModeloMotivoViagemForm`

Esse form expõe apenas:

- `nome`
- `texto`

Não expõe:

- `codigo`
- `ordem`
- `ativo`
- `padrao`

## Ordenação

A ordenação efetivamente usada hoje é por `nome`:

- no `Meta` do model;
- na list view (`order_by('nome')`);
- no queryset do Step 1 (`ModeloMotivoViagem.objects.all().order_by('nome')`).

O campo `ordem` existe, mas não comanda a UI atual.

## Padrão

Como funciona:

- o usuário pode clicar em `Definir como padrão` na lista;
- a view zera `padrao` dos demais;
- marca o escolhido como `padrao=True`;
- no Step 1, se o ofício ainda não tiver modelo salvo, a view tenta pré-selecionar o primeiro `padrao=True`.

## Ativo/inativo

Situação atual:

- o model tem campo `ativo`;
- o CRUD atual não mostra esse campo;
- o `save()` do model força `ativo=True`;
- portanto, hoje não existe fluxo real de inativação pela aplicação.

## Exclusão

Como funciona:

- a exclusão é permitida pela view `modelos_motivo_excluir`;
- não há bloqueio se já existir ofício usando esse modelo;
- como `Oficio.modelo_motivo` é `SET_NULL`, a referência pode cair para `NULL` após exclusão.

## Preenchimento do motivo no ofício

No Step 1:

- o select lista todos os modelos;
- ao escolher um modelo, o JS chama `modelo_motivo_texto_api`;
- a API devolve `{ok, texto, nome}`;
- o textarea `motivo` é substituído pelo texto retornado.

## Retorno ao ofício

As telas de modelos de motivo preservam `volta_step1`.

Isso permite:

- abrir a lista a partir do Step 1;
- cadastrar/editar/excluir/definir padrão;
- voltar ao mesmo ofício via botão `Voltar para Step 1`.

# 13. Custeio

Campo principal:

- `Oficio.custeio_tipo`

Campos auxiliares:

- `Oficio.nome_instituicao_custeio`

Choices atuais:

- `UNIDADE - DPC (diárias e combustível custeados pela DPC).`
- `OUTRA INSTITUIÇÃO`
- `ÔNUS LIMITADOS AOS PRÓPRIOS VENCIMENTOS`

## Regras condicionais

- se o tipo for `OUTRA_INSTITUICAO`, `nome_instituicao_custeio` é obrigatório;
- se não for `OUTRA_INSTITUICAO`, `nome_instituicao_custeio` é limpo pelo form e também pelo model.

## Impacto no fluxo

Hoje o impacto do custeio é:

- validação do Step 1;
- exibição no preview lateral do Step 1;
- exibição no Step 4.

Hoje ele não altera:

- cálculo de diárias;
- regras de Step 2;
- regras de Step 3;
- geração documental, porque ela ainda não existe.

# 14. Viajantes

## Como são selecionados

Step responsável:

- `Step 1`

API:

- `eventos.views.oficio_step1_viajantes_api`

Critérios:

- `status=FINALIZADO`;
- busca por nome, RG e CPF;
- até 20 resultados;
- ordenação por nome.

## Obrigatoriedade

- o Step 1 exige pelo menos um viajante;
- a validação fica no `OficioStep1Form.clean()`.

## Persistência

- os viajantes do ofício são persistidos em `Oficio.viajantes` (`ManyToMany`);
- a ordem de exibição na UI acompanha a ordem dos IDs escondidos no formulário, não um campo de ordem no banco.

## Retorno ao ofício

Cadastro de novo viajante:

- link construído com `cadastros:viajante-cadastrar?next=<url do Step 1>`;
- após salvar, `cadastros.views.viajante_cadastrar` usa `_next_url_safe()` e volta ao Step 1.

Fluxos auxiliares do cadastro de viajante:

- `viajante_salvar_rascunho_ir_cargos`
- `viajante_salvar_rascunho_ir_unidades`

Essas views:

- salvam ou atualizam um viajante em `RASCUNHO`;
- guardam URL de retorno em sessão;
- levam o usuário ao CRUD de cargos/unidades;
- depois o usuário volta a editar o mesmo viajante.

Observação importante:

- `EventoParticipante` não é reaproveitado pelo ofício;
- o ofício mantém lista própria de viajantes.

# 15. Veículo e motorista

## Veículo do ofício

Origem:

- Step 2;
- busca em `cadastros.Veiculo`.

Preenchimento automático:

- ocorre por placa quando existe veículo `FINALIZADO`;
- o backend procura por placa normalizada com `buscar_veiculo_finalizado_por_placa`;
- se encontrado, pode preencher `modelo`, `combustivel` e `tipo_viatura` ausentes.

Persistência:

- `oficio.veiculo_id` guarda o vínculo com o cadastro, se encontrado;
- `oficio.placa`, `oficio.modelo` e `oficio.combustivel` guardam snapshot textual;
- o snapshot continua existindo mesmo que o vínculo com cadastro seja `None`.

## Motorista do ofício

Dois modos:

- motorista cadastrado (via `motorista_viajante`);
- motorista manual (`motorista_nome`).

Regras:

- se o motorista for manual, ele sempre é tratado como carona;
- se o motorista for cadastrado mas não estiver entre os viajantes do ofício, também é carona;
- se estiver entre os viajantes, não é carona.

Campos persistidos:

- `motorista_viajante_id`
- `motorista`
- `motorista_carona`
- `motorista_oficio_numero`
- `motorista_oficio_ano`
- `motorista_oficio`
- `motorista_protocolo`

## Placa

Máscara:

- `ABC-1234` ou `ABC1D23`

Normalização:

- feita em backend por `normalize_placa`;
- usa helpers de `core/utils/masks.py`.

## Validações relevantes

O Step 2 exige:

- `placa`
- `modelo`
- `combustivel`

Se motorista manual:

- exige `motorista_nome`

Se motorista carona:

- exige `motorista_oficio_numero`
- exige `motorista_protocolo`
- preenche `motorista_oficio_ano` com o ano corrente quando necessário

## Carona

No projeto atual, “carona” é um conceito inferido, não um cadastro separado:

- manual = carona;
- servidor fora da lista de viajantes = carona.

O campo `carona_oficio_referencia` existe no model, mas a UI atual não o usa e não pede referência de outro `Oficio` por FK.

# 16. Trechos / roteiros / diárias

## Trechos do ofício

Estrutura atual:

- trechos de ida/intermediários ficam em `OficioTrecho`;
- o retorno fica em campos do próprio `Oficio`.

## Uso de roteiros do evento

O ofício pode usar `RoteiroEvento` como fonte.

O que acontece:

- a view monta opções com `_build_step3_route_options`;
- cada opção tem `id`, `label`, `resumo`, `status` e um estado serializado;
- ao escolher o roteiro, o Step 3 clona os dados para o estado do ofício;
- alterações posteriores no ofício não alteram o `RoteiroEventoTrecho`.

Observação relevante:

- a lista de roteiros disponíveis no Step 3 não filtra por `status`;
- portanto, o ofício pode escolher roteiro do evento em `RASCUNHO` ou `FINALIZADO`.

## Criação própria do roteiro

Quando o usuário escolhe `ROTEIRO_PROPRIO`:

- define sede;
- define destinos dinâmicos;
- o JS reconstrói os cards dos trechos;
- o retorno é calculado como “último destino -> sede”.

## Persistência

No save do Step 3:

- todos os `OficioTrecho` antigos são apagados;
- os novos são recriados em lote;
- `retorno_*` fica em campos do `Oficio`.

## Calculadora de diárias

Service:

- `eventos/services/diarias.py`

Tabelas atuais:

- `INTERIOR`
- `CAPITAL`
- `BRASILIA`

Lógica resumida:

- cada parada é classificada;
- o cálculo usa as saídas para cada parada e a chegada final à sede;
- se o período cruza a data e soma menos de 24h, a função `_segment_breakdown()` considera 1 diária integral;
- sobras entre 6h e 8h geram 15%;
- sobras acima de 8h geram 30%;
- o valor final é multiplicado pela quantidade de servidores (`oficio.viajantes.count()`).

## Tipo de destino

`tipo_destino` do ofício não é digitado manualmente.

Ele é inferido por:

- `infer_tipo_destino_from_paradas(paradas)`

Escalada da classificação:

- se passar por Brasília, o tipo vira `BRASILIA`;
- senão, se passar por capital, vira `CAPITAL`;
- senão, fica `INTERIOR`.

# 17. Status do ofício

Status existentes:

- `RASCUNHO`
- `FINALIZADO`

## Entrada em rascunho

Na criação:

- `guiado_etapa_3_criar_oficio()` cria com `status=RASCUNHO`.

## Transição para finalizado

Na finalização:

- `oficio_step4()` recebe POST com `finalizar=1`;
- salva `status=FINALIZADO`.

## Bloqueios e ausência de bloqueios

Bloqueios que existem:

- apenas as validações locais do POST de cada step.

Bloqueios que não existem:

- não há trava para abrir steps posteriores sem completar anteriores;
- não há trava para editar um ofício finalizado;
- não há trava para excluir um ofício finalizado;
- não há trava de finalização condicionada ao preenchimento completo dos steps.

## Relação com o fluxo do evento

No painel do evento:

- a Etapa 3 fica “OK” se existir qualquer ofício ligado ao evento;
- não depende de ofício finalizado.

# 18. Documentos gerados

## O que existe hoje

No projeto atual, o módulo de ofícios não gera documentos.

Não encontrei implementação atual para:

- gerar arquivo de ofício;
- gerar justificativa;
- gerar plano de trabalho;
- gerar ordem de serviço;
- gerar termos;
- centralizar downloads do ofício;
- armazenar uploads/documentos vinculados ao ofício.

## O que existe apenas como placeholder ou infraestrutura parcial

- `documentos/views.py`: placeholder geral do módulo `Documentos`;
- `documentos/urls.py`: só rota raiz placeholder;
- `templates/eventos/oficio/documentos_placeholder.html`: placeholder antigo, sem rota ativa ligada ao ofício;
- `ConfiguracaoSistema` e `AssinaturaConfiguracao`: já armazenam assinaturas por tipo documental, mas hoje não são consumidos pelo fluxo de ofício;
- `templates/eventos/guiado/painel.html`: etapas 4, 5 e 6 aparecem como `Em breve`.

## O que o ofício efetivamente “gera” hoje

Não gera arquivo, mas passa a persistir:

- `tipo_destino`;
- `quantidade_diarias`;
- `valor_diarias`;
- `valor_diarias_extenso`;
- trechos;
- resumo navegável no Step 4.

# 19. Regras de negócio

- A criação de ofício no fluxo guiado acontece por `GET` ou `POST` em `guiado_etapa_3_criar_oficio`; ambos criam registro.
- O ofício nasce em `RASCUNHO`.
- O número do ofício é anual, usa a menor lacuna disponível e é atribuído na criação do objeto.
- A exclusão de um ofício libera sua lacuna de numeração para reutilização futura no mesmo ano.
- O protocolo do ofício é armazenado sem máscara, com exatamente 9 dígitos.
- O protocolo do Step 1 é obrigatório na UI atual.
- O protocolo do motorista segue a mesma normalização de 9 dígitos quando preenchido.
- O Step 1 exige ao menos um viajante.
- O Step 1 pré-seleciona o modelo de motivo padrão quando o ofício ainda não tem modelo.
- Se um modelo de motivo for escolhido e o campo `motivo` estiver vazio no POST, o form injeta o texto do modelo.
- Se `custeio_tipo=OUTRA_INSTITUICAO`, o nome da instituição é obrigatório.
- Se `custeio_tipo!=OUTRA_INSTITUICAO`, o nome da instituição é sempre limpo.
- O cadastro inline de modelo de motivo no Step 1 exige que o `motivo` atual não esteja vazio.
- O Step 1 usa apenas viajantes finalizados nas buscas, mas preserva IDs já escolhidos mesmo que deixem de estar finalizados depois.
- O Step 2 usa apenas veículos finalizados nas buscas.
- O Step 2 usa apenas viajantes finalizados como candidatos a motorista.
- O Step 2 exige placa, modelo e combustível.
- Se a placa existir no cadastro finalizado, o backend pode completar modelo, combustível e tipo de viatura que vierem vazios.
- O tipo de viatura do ofício usa mapeamento do tipo do veículo cadastrado.
- `porte_transporte_armas` assume `True` por default quando nada válido foi enviado.
- Motorista manual é sempre tratado como carona.
- Motorista cadastrado fora da lista de viajantes do ofício também é tratado como carona.
- Motorista carona exige número do ofício do motorista e protocolo do motorista.
- Quando o motorista não é carona, os campos de carona são zerados.
- No Step 3 em modo `EVENTO_EXISTENTE`, a escolha do roteiro é obrigatória.
- O roteiro do evento selecionado precisa pertencer ao mesmo evento do ofício.
- O Step 3 exige sede completa: estado e cidade.
- A cidade da sede deve pertencer ao estado selecionado.
- O Step 3 exige pelo menos um destino.
- Cada destino deve referenciar cidade ativa pertencente ao estado ativo informado.
- Cada trecho exige saída e chegada.
- A chegada do trecho não pode ser anterior à saída.
- O retorno exige saída e chegada.
- A chegada do retorno não pode ser anterior à saída.
- `tempo_adicional_min` nunca fica negativo no backend do Step 3.
- O retorno do ofício é salvo em campos do `Oficio`, não como `OficioTrecho`.
- O save do Step 3 apaga e recria todos os trechos do ofício.
- O cálculo de diárias exige pelo menos um viajante no Step 1.
- O cálculo de diárias usa paradas do roteiro e a chegada final à sede.
- `tipo_destino` é derivado do roteiro/diárias, não digitado manualmente.
- O Step 4 finaliza o ofício apenas mudando o status para `FINALIZADO`.
- Não há trava para reabrir e editar um ofício finalizado.
- Não há trava para excluir um ofício finalizado.
- A lista da Etapa 3 do evento não mostra central de documentos.
- `ModeloMotivoViagem.ativo` é sempre forçado para `True` no `save()`.
- O campo `ordem` do modelo de motivo existe, mas não é o critério real de ordenação da UI atual.
- A exclusão de modelo de motivo não é bloqueada por uso em ofícios já existentes.
- O campo `carona_oficio_referencia` existe no model, mas não participa do fluxo real.

# 20. Dependências com outros módulos

## Dependência com `eventos` (nível evento/roteiro)

- o ofício nasce dentro da Etapa 3 de um evento;
- usa `Evento` como contêiner do fluxo;
- usa `EventoDestino` como pré-preenchimento quando não há roteiro do evento;
- usa `RoteiroEvento`, `RoteiroEventoDestino` e `RoteiroEventoTrecho` como fonte alternativa para o Step 3;
- o painel do evento define status da etapa com `_evento_etapa3_ok`.

## Dependência com `cadastros`

- `Viajante`: Step 1 e motoristas do Step 2;
- `Veiculo`: Step 2;
- `CombustivelVeiculo`: datalist do Step 2;
- `Cargo`: enriquecimento do preview de viajantes/motoristas;
- `UnidadeLotacao`: regra de completude do viajante;
- `Estado` e `Cidade`: Step 3, evento, roteiros e estimativa local;
- `ConfiguracaoSistema`: fallback de `cidade_sede_padrao`;
- `AssinaturaConfiguracao`: infraestrutura existente para assinaturas futuras, ainda não consumida pelo ofício atual.

## Dependência com `core`

- autenticação: todas as views relevantes usam `login_required`;
- máscaras canônicas: `core/utils/masks.py`;
- `only_digits`, formatação de protocolo e placa;
- `EMPTY_MASK_DISPLAY` para exibição consistente.

## Dependência com JS estático

- `static/js/masks.js` aplica máscara progressiva aos campos visuais;
- os templates do wizard têm JS embutido para comportamento de busca, preview, renderização dinâmica e chamadas AJAX.

## Dependência com `documentos`

Praticamente inexistente no fluxo atual.

O app `documentos`:

- não tem model funcional de documento do ofício;
- não tem rota de central de documentos do ofício;
- não é chamado pelo hub nem pelo Step 4.

## Dependências que hoje não existem

Não encontrei integração atual de ofícios com:

- uploads/arquivos;
- justificativas reais;
- termos reais;
- plano de trabalho real;
- ordem de serviço real.

# 21. Pontos fortes e pontos frágeis do módulo

## Pontos fortes

- O módulo está claramente organizado em steps, o que separa bem dados gerais, transporte, roteiro e resumo.
- A numeração anual com menor lacuna disponível e retry por concorrência é uma regra consistente e bem encapsulada no model.
- A normalização de protocolo e placa é coerente entre backend e frontend.
- O Step 3 preserva a independência do ofício: usar roteiro do evento não corrompe o roteiro fonte.
- O cálculo de diárias está centralizado em service próprio, não espalhado por template.
- O fluxo de retorno para cadastro de viajante e veículo via `next` está funcional e coberto por testes.
- Há boa cobertura de testes para os pontos mais sensíveis do wizard atual: protocolo, numeração, carona, roteiros e diárias.

## Pontos frágeis

- `eventos/views.py` tem duplicidade de funções e views do Step 3/4; isso aumenta muito o risco de manutenção e leitura incorreta.
- `guiado_etapa_3_criar_oficio()` altera estado por `GET`, o que não é uma prática segura para criação de registro.
- O Step 4 finaliza sem revalidar completude do ofício.
- Um ofício `FINALIZADO` continua editável nos Steps 1-3 e também continua excluível.
- O painel do evento considera a Etapa 3 “OK” apenas pela existência de um ofício, não pela qualidade/completude dele.
- O Step 3 permite selecionar roteiros do evento ainda em `RASCUNHO`.
- A central de documentos e os módulos documentais prometidos no fluxo ainda não existem.
- `ModeloMotivoViagem` tem campos `ativo` e `ordem` que não se comportam como a UI sugere: `ativo` nunca fica `False` e `ordem` não ordena a listagem.
- O campo `carona_oficio_referencia` está sem uso prático no fluxo atual.
- O save do Step 3 apaga e recria trechos, o que elimina estabilidade de IDs e qualquer possibilidade de auditoria incremental desses itens.
- Existem templates placeholder antigos de edição/documentos que ficaram no repositório sem uso no runtime atual.

# 22. Resumo executivo

O módulo atual de ofícios de viagem já entrega um fluxo operacional completo de cadastro em 4 steps: criação do ofício dentro do evento, dados gerais, viajantes, transporte, motorista, roteiro, retorno, cálculo de diárias, resumo e finalização. O núcleo real está em `eventos/models.py`, `eventos/forms.py`, `eventos/views.py` e nos templates `templates/eventos/oficio/wizard_step1.html` a `wizard_step4.html`.

Hoje o módulo é fortemente integrado a evento, roteiro do evento, cadastro de viajantes, cadastro de veículos, base geográfica e configuração sistêmica de sede. O Step 3 é a parte mais complexa: ele reaproveita roteiros do evento quando existem, também permite roteiro próprio, calcula estimativa local de km/tempo sem API externa e grava as diárias consolidadas no próprio `Oficio`.

Ao mesmo tempo, o escopo atual para no cadastro. Não há central de documentos funcional, nem geração real de ofício, justificativa, termos, plano de trabalho ou ordem de serviço. Também não há travas fortes de progressão/finalização: o sistema deixa finalizar sem revalidação global e deixa reabrir um ofício já finalizado.

Em termos práticos, o estado atual do módulo é:

- forte para cadastro operacional e composição da viagem;
- razoavelmente bom em consistência de máscaras, numeração e cálculo de diárias;
- incompleto na camada documental;
- frágil em governança de status, criação via GET e duplicidade de código em `eventos/views.py`.
