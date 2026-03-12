# Relatorio Final da Validacao Cega da Estimativa de Viagem do Parana

## 1. Resumo executivo

- A arquitetura segue correta como software: provider route-aware, fallback funcional, ETA tecnico separado do buffer e interface publica preservada.
- A validacao cega fora da amostra nao confirmou generalizacao satisfatoria.
- Ha indicio forte de overfitting nas 15 rotas usadas no benchmark calibrado.
- Status final: precisa recalibrar.

Em numeros, o benchmark calibrado ficou em MAE `1,67 min`, p95 `4,0 min` e `100%` das rotas dentro de 15 min. Na validacao cega, o mesmo estimador route-aware caiu para MAE `15,94 min`, p95 `38,0 min` e apenas `52,94%` dentro de 15 min. O fallback manteve o sistema operacional, mas com desempenho pior: MAE `29,47 min`, p95 `82,0 min`.

## 2. Contexto da avaliacao

O benchmark calibrado e o conjunto oficial de 15 rotas reais do Parana usado para ajustar e conferir a calibracao local. Ele mede o ETA tecnico do sistema contra referencias externas e representa a amostra "vista" no processo de calibracao.

A validacao cega e um conjunto novo, fora da amostra, montado para testar generalizacao real. Nesta etapa foram avaliadas 17 rotas novas, todas fora do benchmark calibrado, com foco em litoral, campos gerais, norte, noroeste, oeste, sudoeste e sul.

Esta etapa foi feita para responder uma pergunta simples: o modelo calibrado nas 15 rotas oficiais continua bom quando sai da amostra? A resposta, pelos dados obtidos, e nao.

Conjuntos avaliados:

| Conjunto | Objetivo | Rotas |
| --- | --- | ---: |
| Benchmark calibrado | medir desempenho na amostra usada para calibracao | 15 |
| Validacao cega | medir generalizacao fora da amostra | 17 |

Arquivos de referencia localizados:

- `data/rotas_pr_benchmark.json`
- `data/rotas_pr_calibracao.json`
- `data/rotas_pr_validacao_cega.json`
- `data/relatorio_estimativa_pr_coleta.json`
- `data/relatorio_validacao_cega.json`
- `scripts/analisar_estimativa_pr.py`
- `scripts/validar_estimativa_pr_cega.py`

Arquivo nao localizado com esse nome:

- `data/rotas_pr_referencias_validacao.json`

Equivalente usado:

- As referencias externas da validacao cega estao embutidas em `data/rotas_pr_validacao_cega.json` e repetidas em `data/relatorio_validacao_cega.json`, com `tempo_referencia_min`, `distancia_referencia_km`, `fonte_referencia`, `fonte_link`, `data_coleta` e `metodo_coleta`.

## 3. Resultado dos testes automaticos

### Validacoes executadas

| Comando | Resultado |
| --- | --- |
| `python manage.py check` | OK, sem issues |
| `python manage.py test eventos.tests.test_eventos.EstimativaLocalServiceTest` | OK, `25` testes |
| `python manage.py test eventos.tests.test_eventos` | OK, `325` testes |
| `python scripts/analisar_estimativa_pr.py` | OK, benchmark calibrado revalidado |
| `python scripts/validar_estimativa_pr_cega.py` | OK, validacao cega gerada |

### Observacoes relevantes

- `python manage.py check`: `System check identified no issues (0 silenced).`
- `EstimativaLocalServiceTest`: `25` testes, todos passando, sem regressao funcional na estimativa.
- `eventos.tests.test_eventos`: `325` testes, todos passando. Houve warnings antigos de `DateTimeField ... received a naive datetime while time zone support is active`; nao viraram falha e nao indicam regressao da estimativa.
- O ambiente emitiu tambem o warning de configuracao `.env` ausente em `config/settings.py`; isso nao impediu execucao nem alterou a logica medida.
- `scripts/analisar_estimativa_pr.py`: benchmark calibrado permaneceu excelente, com provider `demo (https://router.project-osrm.org)`.
- `scripts/validar_estimativa_pr_cega.py`: executou os cenarios route-aware e fallback sem quebrar o sistema e salvou `data/relatorio_validacao_cega.json` e `data/relatorio_validacao_cega.md`.

Conclusao da regressao: nao houve regressao de software. O problema observado e de generalizacao estatistica, nao de quebra funcional.

## 4. Tabela completa da validacao cega

Tabela abaixo usa o cenario principal route-aware, comparando o ETA tecnico do sistema com a referencia externa.

| origem | destino | km_sys | ETA tecnico | buffer | total | corredor_macro | corredor_fino | refs_predominantes | rota_fonte | fallback_usado | confianca_estimativa | km_ref | tempo_ref | fonte_ref | erro ETA | erro abs ETA | erro total | erro abs total |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| Curitiba | Toledo | 542.3 | 420 | 10 | 430 | BR277_OESTE | TOLEDO | BR-277, BR-467, PRC-467 | OSRM | False | alta | 540.4 | 427 | Rome2Rio (opcao Drive) | -7.0 | 7.0 | +3.0 | 3.0 |
| Curitiba | Campo Mourao | 456.5 | 380 | 15 | 395 | NOROESTE_INTERIOR | CAMPO_MOURAO | BR-277, PRC-466, BR-487, PR-460 | OSRM | False | alta | 450.2 | 365 | Rome2Rio (opcao Drive) | +15.0 | 15.0 | +30.0 | 30.0 |
| Curitiba | Paranavai | 499.5 | 400 | 15 | 415 | NOROESTE_INTERIOR | PARANAVAI | BR-376, BR-277, PR-897, PR-151 | OSRM | False | alta | 500.5 | 381 | Rome2Rio (opcao Drive) | +19.0 | 19.0 | +34.0 | 34.0 |
| Curitiba | Jacarezinho | 387.6 | 280 | 15 | 295 | NORTE_CAFE | JACAREZINHO | BR-153, BR-277, PR-151, PR-090 | OSRM | False | alta | 351.5 | 307 | Rome2Rio (opcao Drive) | -27.0 | 27.0 | -12.0 | 12.0 |
| Curitiba | Uniao da Vitoria | 237.1 | 170 | 10 | 180 | CAMPOS_GERAIS | UNIAO_DA_VITORIA | BR-476, PR-835, BR-277, BR-153 | OSRM | False | alta | 232.6 | 208 | Rome2Rio (opcao Drive) | -38.0 | 38.0 | -28.0 | 28.0 |
| Curitiba | Pato Branco | 452.6 | 320 | 10 | 330 | BR277_OESTE | PATO_BRANCO | BR-476, PRC-280, BR-153, BR-277 | OSRM | False | alta | 435.5 | 351 | Rome2Rio (opcao Drive) | -31.0 | 31.0 | -21.0 | 21.0 |
| Curitiba | Irati | 155.5 | 115 | 10 | 125 | CAMPOS_GERAIS | IRATI | BR-277, BR-153 | OSRM | False | alta | 152.6 | 119 | Rome2Rio (opcao Drive) | -4.0 | 4.0 | +6.0 | 6.0 |
| Curitiba | Castro | 159.9 | 110 | 10 | 120 | CAMPOS_GERAIS | CASTRO | BR-277, PR-151, BR-376, PRC-373 | OSRM | False | alta | 147.9 | 122 | Rome2Rio (opcao Drive) | -12.0 | 12.0 | -2.0 | 2.0 |
| Curitiba | Guaratuba | 119.8 | 115 | 5 | 120 | BR277_LITORAL | GUARATUBA | BR-277, PR-508, PR-412, PR-806 | OSRM | False | alta | 130.8 | 111 | Rome2Rio (opcao Drive) | +4.0 | 4.0 | +9.0 | 9.0 |
| Curitiba | Matinhos | 111.1 | 90 | 5 | 95 | BR277_LITORAL | MATINHOS | BR-277, PR-508, PR-412 | OSRM | False | alta | 110.6 | 77 | Rome2Rio (opcao Drive) | +13.0 | 13.0 | +18.0 | 18.0 |
| Curitiba | Ivaipora | 380.3 | 300 | 10 | 310 | BR277_OESTE | PADRAO | BR-277, BR-376, PRC-487, PR-239 | OSRM | False | alta | 356.0 | 322 | Rome2Rio (opcao Drive) | -22.0 | 22.0 | -12.0 | 12.0 |
| Curitiba | Loanda | 579.5 | 450 | 15 | 465 | NORTE_CAFE | PADRAO | BR-376, BR-277, PR-182, PR-897 | OSRM | False | alta | 577.3 | 447 | Rome2Rio (opcao Drive) | +3.0 | 3.0 | +18.0 | 18.0 |
| Curitiba | Guaira | 643.5 | 505 | 10 | 515 | BR277_OESTE | PADRAO | BR-277, BR-467, PRC-467, BR-163 | OSRM | False | alta | 608.5 | 474 | Rome2Rio (opcao Drive) | +31.0 | 31.0 | +41.0 | 41.0 |
| Curitiba | Medianeira | 580.4 | 450 | 10 | 460 | BR277_OESTE | PADRAO | BR-277, PR-495 | OSRM | False | alta | 577.0 | 450 | Rome2Rio (opcao Drive) | +0.0 | 0.0 | +10.0 | 10.0 |
| Curitiba | Santo Antonio da Platina | 365.2 | 265 | 15 | 280 | NORTE_CAFE | JACAREZINHO | BR-153, BR-277, PR-151, PR-090 | OSRM | False | alta | 330.5 | 288 | Rome2Rio (opcao Drive) | -23.0 | 23.0 | -8.0 | 8.0 |
| Curitiba | Cornelio Procopio | 400.3 | 305 | 15 | 320 | NORTE_CAFE | PADRAO | BR-277, PR-151, PR-435, PR-090 | OSRM | False | alta | 366.2 | 324 | Rome2Rio (opcao Drive) | -19.0 | 19.0 | -4.0 | 4.0 |
| Curitiba | Marechal Candido Rondon | 580.7 | 445 | 10 | 455 | BR277_OESTE | PADRAO | BR-277, BR-467, PRC-467, BR-163 | OSRM | False | alta | 577.2 | 448 | Rome2Rio (opcao Drive) | -3.0 | 3.0 | +7.0 | 7.0 |

## 5. Metricas gerais da validacao cega

### Cenario principal route-aware

| Metrica | Valor |
| --- | ---: |
| Quantidade total de rotas | 17 |
| MAE ETA | 15.94 |
| RMSE ETA | 19.50 |
| Mediana do erro absoluto | 15.0 |
| p50 | 15.0 |
| p95 | 38.0 |
| p99 | 38.0 |
| % dentro de 5 min | 29.41% |
| % dentro de 10 min | 35.29% |
| % dentro de 15 min | 52.94% |
| Maior erro positivo | Curitiba -> Guaira (+31.0) |
| Maior erro negativo | Curitiba -> Uniao da Vitoria (-38.0) |

### Cenario fallback

| Metrica | Valor |
| --- | ---: |
| Quantidade total de rotas | 17 |
| MAE ETA | 29.47 |
| RMSE ETA | 39.31 |
| Mediana do erro absoluto | 17.0 |
| p50 | 17.0 |
| p95 | 82.0 |
| p99 | 82.0 |
| % dentro de 5 min | 17.65% |
| % dentro de 10 min | 35.29% |
| % dentro de 15 min | 41.18% |
| Maior erro positivo | Curitiba -> Marechal Candido Rondon (+82.0) |
| Maior erro negativo | Curitiba -> Santo Antonio da Platina (-33.0) |

Leitura tecnica: o route-aware foi melhor que o fallback, mas ainda ficou distante do patamar desejado. O fallback serve como degradacao limpa; nao serve como resultado competitivo de acuracia.

## 6. Comparacao benchmark calibrado vs validacao cega

| Metrica | Benchmark calibrado | Validacao cega |
| --- | ---: | ---: |
| Numero de rotas | 15 | 17 |
| MAE | 1.67 | 15.94 |
| RMSE | 2.14 | 19.50 |
| p95 | 4.0 | 38.0 |
| % dentro de 10 min | 100.0% | 35.29% |
| % dentro de 15 min | 100.0% | 52.94% |
| Maior erro absoluto | 4.0 | 38.0 |
| Maior erro positivo | Palotina (+4.0) | Guaira (+31.0) |
| Maior erro negativo | Guarapuava (-4.0) | Uniao da Vitoria (-38.0) |

Principais corredores no benchmark calibrado:

- BR277_LITORAL: MAE `0.5`
- CAMPOS_GERAIS: MAE `1.0`
- NORTE_CAFE: MAE `0.67`
- NOROESTE_INTERIOR: MAE `1.67`
- BR277_OESTE: MAE `3.0`

Principais corredores na validacao cega:

- BR277_LITORAL: MAE `8.5`
- BR277_OESTE: MAE `15.67`
- CAMPOS_GERAIS: MAE `18.0`
- NOROESTE_INTERIOR: MAE `17.0`
- NORTE_CAFE: MAE `18.0`

Respostas objetivas:

- A performance se manteve? Nao.
- Caiu pouco? Nao.
- Caiu muito? Sim.
- Houve generalizacao real? Nao.
- Ha indicio de overfitting? Sim, forte.

Justificativa: o delta entre benchmark e validacao cega foi de `+14.27 min` em MAE, `+34.0 min` em p95 e `-47.06 p.p.` em rotas dentro de 15 min. Isso e grande demais para ser tratado como variacao normal.

## 7. Analise por corredor

### Por corredor_macro

| corredor_macro | quantidade | erro medio | erro absoluto medio | maior erro | tendencia |
| --- | ---: | ---: | ---: | --- | --- |
| BR277_LITORAL | 2 | +8.50 | 8.50 | Curitiba -> Matinhos (+13.0) | superestima |
| BR277_OESTE | 6 | -5.33 | 15.67 | Curitiba -> Pato Branco (-31.0) | subestima |
| CAMPOS_GERAIS | 3 | -18.00 | 18.00 | Curitiba -> Uniao da Vitoria (-38.0) | subestima |
| NOROESTE_INTERIOR | 2 | +17.00 | 17.00 | Curitiba -> Paranavai (+19.0) | superestima |
| NORTE_CAFE | 4 | -16.50 | 18.00 | Curitiba -> Jacarezinho (-27.0) | subestima |

Leitura:

- Litoral generalizou relativamente melhor que os demais corredores, embora ainda acima do benchmark.
- BR277_OESTE continuou instavel, com mistura de superestimacao e subestimacao e varios casos em `PADRAO`.
- CAMPOS_GERAIS e NORTE_CAFE foram os piores blocos da validacao cega, ambos com MAE `18.0`.

### Por corredor_fino

| corredor_fino | quantidade | erro medio | erro absoluto medio | maior erro | tendencia |
| --- | ---: | ---: | ---: | --- | --- |
| CAMPO_MOURAO | 1 | +15.00 | 15.00 | Curitiba -> Campo Mourao (+15.0) | superestima |
| CASTRO | 1 | -12.00 | 12.00 | Curitiba -> Castro (-12.0) | subestima |
| GUARATUBA | 1 | +4.00 | 4.00 | Curitiba -> Guaratuba (+4.0) | superestima |
| IRATI | 1 | -4.00 | 4.00 | Curitiba -> Irati (-4.0) | subestima |
| JACAREZINHO | 2 | -25.00 | 25.00 | Curitiba -> Jacarezinho (-27.0) | subestima |
| MATINHOS | 1 | +13.00 | 13.00 | Curitiba -> Matinhos (+13.0) | superestima |
| PADRAO | 6 | -1.67 | 13.00 | Curitiba -> Guaira (+31.0) | subestima media, mas instavel |
| PARANAVAI | 1 | +19.00 | 19.00 | Curitiba -> Paranavai (+19.0) | superestima |
| PATO_BRANCO | 1 | -31.00 | 31.00 | Curitiba -> Pato Branco (-31.0) | subestima |
| TOLEDO | 1 | -7.00 | 7.00 | Curitiba -> Toledo (-7.0) | subestima |
| UNIAO_DA_VITORIA | 1 | -38.00 | 38.00 | Curitiba -> Uniao da Vitoria (-38.0) | subestima |

Leitura:

- `JACAREZINHO`, `PATO_BRANCO` e `UNIAO_DA_VITORIA` foram corredores finos claramente ruins fora da amostra.
- O grupo `PADRAO` ainda recebeu 6 rotas na validacao cega, o que sugere classificacao fina insuficiente em parte relevante do interior.

### Por rota_fonte

| rota_fonte | quantidade | erro medio | erro absoluto medio | maior erro | tendencia |
| --- | ---: | ---: | ---: | --- | --- |
| OSRM (route-aware) | 17 | -5.94 | 15.94 | Curitiba -> Uniao da Vitoria (-38.0) | subestima |
| ESTIMATIVA_LOCAL (fallback) | 17 | +21.12 | 29.47 | Curitiba -> Marechal Candido Rondon (+82.0) | superestima |

Leitura:

- O provider route-aware funcionou e foi melhor que o fallback.
- O fallback continuou coerente como degradacao, mas com erro alto demais para servir como resultado comparavel ao cenario principal.

## 8. Validacao da arquitetura

Confirmacoes objetivas a partir de `data/relatorio_validacao_cega.json`:

- ETA tecnico continua separado do buffer: `True` em `100%` das rotas route-aware e fallback.
- `duracao_estimada_min = tempo_viagem_estimado_min + buffer_operacional_sugerido_min`: `True` em `100%` das rotas route-aware e fallback.
- O campo comparavel ao Maps continua sendo o ETA tecnico: a comparacao da validacao cega foi feita com `tempo_viagem_estimado_min`, nao com o total planejado.
- O fallback funciona sem quebrar: `17/17` rotas responderam com os campos antigos e novos presentes.
- O provider route-aware funciona quando disponivel: `17/17` rotas do cenario principal sairam com `rota_fonte = OSRM` e `fallback_usado = False`.

Conclusao arquitetural: o sistema esta correto como software. O problema atual nao e separacao de camadas nem degradacao; e acuracia fora da amostra.

## 9. Problemas encontrados

- A validacao cega ficou muito pior que o benchmark calibrado.
- O cenario route-aware desta medicao usou o demo publico do OSRM, nao um OSRM local dedicado.
- `NORTE_CAFE` e `CAMPOS_GERAIS` tiveram MAE `18.0`, com clara tendencia de subestimar.
- `BR277_OESTE` continuou instavel e ainda teve muitas rotas indo para `PADRAO`.
- `JACAREZINHO`, `PATO_BRANCO` e `UNIAO_DA_VITORIA` ficaram especialmente ruins fora da amostra.
- A confianca veio como `alta` em todas as rotas route-aware, inclusive em casos com erro de `31` a `38` minutos; isso sugere calibracao de confianca excessivamente otimista.
- As referencias externas da validacao cega foram coletadas manualmente em fonte unica (`Rome2Rio`) em `2026-03-11`. Isso limita a robustez do "ground truth", embora nao explique sozinho a degradacao grande observada.
- A amostra cega tem `17` rotas. Ela ja e suficiente para mostrar degradacao relevante, mas ainda nao e grande o bastante para fechar mapa estatistico completo do estado.

## 10. Conclusao honesta

Status final: precisa recalibrar.

Justificativa direta: o modelo ficou excelente dentro da amostra calibrada, mas nao sustentou o mesmo patamar fora dela. A queda de MAE de `1.67` para `15.94`, de p95 de `4.0` para `38.0` e de `%<=15` de `100%` para `52.94%` e forte demais para aprovar o modelo como generalizado. O sistema continua correto e operacional, mas a acuracia fora da amostra ainda nao e confiavel o bastante para ser tratada como resolvida.

## 11. Proximo passo recomendado

Recalibrar.

Escolha de um unico proximo passo principal: recalibrar usando split fixo treino/validacao e preservando um conjunto cego que nao seja tocado durante os ajustes.

## 12. Arquivos usados/criados

### Arquivos lidos

- `data/rotas_pr_benchmark.json`
- `data/rotas_pr_calibracao.json`
- `data/rotas_pr_validacao_cega.json`
- `data/relatorio_estimativa_pr_coleta.json`
- `data/relatorio_validacao_cega.json`
- `scripts/analisar_estimativa_pr.py`
- `scripts/validar_estimativa_pr_cega.py`

### Arquivos auxiliares criados

- `data/rotas_pr_validacao_cega.json`
- `data/relatorio_validacao_cega.json`
- `data/relatorio_validacao_cega.md`
- `data/relatorio_final_validacao_cega.md`

### Scripts usados

- `python manage.py check`
- `python manage.py test eventos.tests.test_eventos.EstimativaLocalServiceTest`
- `python manage.py test eventos.tests.test_eventos`
- `python scripts/analisar_estimativa_pr.py`
- `python scripts/validar_estimativa_pr_cega.py`

### Saidas geradas

- Relatorio tecnico estruturado da validacao cega: `data/relatorio_validacao_cega.json`
- Relatorio resumido da validacao cega: `data/relatorio_validacao_cega.md`
- Relatorio final consolidado desta entrega: `data/relatorio_final_validacao_cega.md`
