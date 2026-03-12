# 1. Resumo executivo
- Rotas cegas: 17
- Provider route-aware: demo (https://router.project-osrm.org)
- Route-aware: MAE 15.94 min, p95 38.0 min, <=15 52.94%
- Fallback: MAE 29.47 min, p95 82.0 min, <=15 41.18%
- Recomendacao: precisa recalibrar
- Conclusao: A validacao cega ficou muito abaixo do benchmark calibrado.

# 2. Rotas da validacao cega
| Rota | Regiao | Tempo ref | Km ref | Fonte | Coleta |
| --- | --- | ---: | ---: | --- | --- |
| Curitiba -> Toledo | oeste | 427 | 540.4 | [link](https://www.rome2rio.com/s/Curitiba/Toledo-Brasil) | manual em 2026-03-11 |
| Curitiba -> Campo Mourao | centro-oeste | 365 | 450.2 | [link](https://www.rome2rio.com/s/Curitiba/Campo-Mour%C3%A3o) | manual em 2026-03-11 |
| Curitiba -> Paranavai | noroeste | 381 | 500.5 | [link](https://www.rome2rio.com/s/Curitiba/Paranava%C3%AD) | manual em 2026-03-11 |
| Curitiba -> Jacarezinho | norte_pioneiro | 307 | 351.5 | [link](https://www.rome2rio.com/s/Curitiba/Jacarezinho) | manual em 2026-03-11 |
| Curitiba -> Uniao da Vitoria | sul | 208 | 232.6 | [link](https://www.rome2rio.com/s/Curitiba/Uni%C3%A3o-da-Vit%C3%B3ria) | manual em 2026-03-11 |
| Curitiba -> Pato Branco | sudoeste | 351 | 435.5 | [link](https://www.rome2rio.com/s/Curitiba/Pato-Branco) | manual em 2026-03-11 |
| Curitiba -> Irati | centro-sul | 119 | 152.6 | [link](https://www.rome2rio.com/s/Curitiba/Irati) | manual em 2026-03-11 |
| Curitiba -> Castro | campos_gerais | 122 | 147.9 | [link](https://www.rome2rio.com/s/Curitiba/Castro) | manual em 2026-03-11 |
| Curitiba -> Guaratuba | litoral | 111 | 130.8 | [link](https://www.rome2rio.com/s/Curitiba/Guaratuba) | manual em 2026-03-11 |
| Curitiba -> Matinhos | litoral | 77 | 110.6 | [link](https://www.rome2rio.com/s/Curitiba/Matinhos) | manual em 2026-03-11 |
| Curitiba -> Ivaipora | norte_central | 322 | 356.0 | [link](https://www.rome2rio.com/s/Curitiba/Ivaipor%C3%A3) | manual em 2026-03-11 |
| Curitiba -> Loanda | noroeste | 447 | 577.3 | [link](https://www.rome2rio.com/s/Curitiba/Loanda) | manual em 2026-03-11 |
| Curitiba -> Guaira | extremo_oeste | 474 | 608.5 | [link](https://www.rome2rio.com/s/Curitiba/Gua%C3%ADra) | manual em 2026-03-11 |
| Curitiba -> Medianeira | oeste | 450 | 577.0 | [link](https://www.rome2rio.com/s/Curitiba/Medianeira) | manual em 2026-03-11 |
| Curitiba -> Santo Antonio da Platina | norte_pioneiro | 288 | 330.5 | [link](https://www.rome2rio.com/s/Curitiba/Santo-Ant%C3%B4nio-da-Platina) | manual em 2026-03-11 |
| Curitiba -> Cornelio Procopio | norte_pioneiro | 324 | 366.2 | [link](https://www.rome2rio.com/s/Curitiba/Corn%C3%A9lio-Proc%C3%B3pio) | manual em 2026-03-11 |
| Curitiba -> Marechal Candido Rondon | oeste | 448 | 577.2 | [link](https://www.rome2rio.com/s/Curitiba/Marechal-C%C3%A2ndido-Rondon) | manual em 2026-03-11 |

# 3. Tabela completa dos resultados
| Destino | Km ref | T ref | ETA OSRM | Buf OSRM | Total OSRM | Erro ETA OSRM | ETA fallback | Buf fallback | Total fallback | Erro ETA fallback | Macro/Fino | Refs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Toledo | 540.4 | 427 | 420 | 10 | 430 | -7.0 | 465 | 10 | 475 | +38.0 | BR277_OESTE/TOLEDO | BR-277, BR-467, PRC-467 |
| Campo Mourao | 450.2 | 365 | 380 | 15 | 395 | +15.0 | 370 | 15 | 385 | +5.0 | NOROESTE_INTERIOR/CAMPO_MOURAO | BR-277, PRC-466, BR-487 |
| Paranavai | 500.5 | 381 | 400 | 15 | 415 | +19.0 | 450 | 15 | 465 | +69.0 | NOROESTE_INTERIOR/PARANAVAI | BR-376, BR-277, PR-897 |
| Jacarezinho | 351.5 | 307 | 280 | 15 | 295 | -27.0 | 300 | 15 | 315 | -7.0 | NORTE_CAFE/JACAREZINHO | BR-153, BR-277, PR-151 |
| Uniao da Vitoria | 232.6 | 208 | 170 | 10 | 180 | -38.0 | 225 | 10 | 235 | +17.0 | CAMPOS_GERAIS/UNIAO_DA_VITORIA | BR-476, PR-835, BR-277 |
| Pato Branco | 435.5 | 351 | 320 | 10 | 330 | -31.0 | 350 | 10 | 360 | -1.0 | BR277_OESTE/PATO_BRANCO | BR-476, PRC-280, BR-153 |
| Irati | 152.6 | 119 | 115 | 10 | 125 | -4.0 | 155 | 10 | 165 | +36.0 | CAMPOS_GERAIS/IRATI | BR-277, BR-153 |
| Castro | 147.9 | 122 | 110 | 10 | 120 | -12.0 | 115 | 5 | 120 | -7.0 | CAMPOS_GERAIS/CASTRO | BR-277, PR-151, BR-376 |
| Guaratuba | 130.8 | 111 | 115 | 5 | 120 | +4.0 | 95 | 5 | 100 | -16.0 | BR277_LITORAL/GUARATUBA | BR-277, PR-508, PR-412 |
| Matinhos | 110.6 | 77 | 90 | 5 | 95 | +13.0 | 90 | 5 | 95 | +13.0 | BR277_LITORAL/MATINHOS | BR-277, PR-508, PR-412 |
| Ivaipora | 356.0 | 322 | 300 | 10 | 310 | -22.0 | 315 | 15 | 330 | -7.0 | BR277_OESTE/PADRAO | BR-277, BR-376, PRC-487 |
| Loanda | 577.3 | 447 | 450 | 15 | 465 | +3.0 | 520 | 15 | 535 | +73.0 | NORTE_CAFE/PADRAO | BR-376, BR-277, PR-182 |
| Guaira | 608.5 | 474 | 505 | 10 | 515 | +31.0 | 530 | 10 | 540 | +56.0 | BR277_OESTE/PADRAO | BR-277, BR-467, PRC-467 |
| Medianeira | 577.0 | 450 | 450 | 10 | 460 | +0.0 | 490 | 10 | 500 | +40.0 | BR277_OESTE/PADRAO | BR-277, PR-495 |
| Santo Antonio da Platina | 330.5 | 288 | 265 | 15 | 280 | -23.0 | 255 | 10 | 265 | -33.0 | NORTE_CAFE/JACAREZINHO | BR-153, BR-277, PR-151 |
| Cornelio Procopio | 366.2 | 324 | 305 | 15 | 320 | -19.0 | 325 | 15 | 340 | +1.0 | NORTE_CAFE/PADRAO | BR-277, PR-151, PR-435 |
| Marechal Candido Rondon | 577.2 | 448 | 445 | 10 | 455 | -3.0 | 530 | 15 | 545 | +82.0 | BR277_OESTE/PADRAO | BR-277, BR-467, PRC-467 |

# 4. Metricas gerais
**Route-aware**

- MAE: 15.94 min
- RMSE: 19.5 min
- Mediana abs: 15.0 min
- p50/p95/p99: 15.0 / 38.0 / 38.0 min
- <=5/10/15 min: 29.41% / 35.29% / 52.94%
- Maior erro positivo: Curitiba -> Guaira (31.0 min)
- Maior erro negativo: Curitiba -> Uniao da Vitoria (-38.0 min)

**Fallback**

- MAE: 29.47 min
- RMSE: 39.31 min
- Mediana abs: 17.0 min
- p50/p95/p99: 17.0 / 82.0 / 82.0 min
- <=5/10/15 min: 17.65% / 35.29% / 41.18%
- Maior erro positivo: Curitiba -> Marechal Candido Rondon (82.0 min)
- Maior erro negativo: Curitiba -> Santo Antonio da Platina (-33.0 min)

# 5. Comparacao com benchmark calibrado
- Benchmark calibrado MAE/p95/<=15: 1.67 / 4.0 / 100.0
- Validacao cega MAE/p95/<=15: 15.94 / 38.0 / 52.94
- Delta MAE: 14.27 min
- Delta p95: 34.0 min
- Delta <=15: -47.06 p.p.

# 6. Analise por corredor
- Corredor macro: [{"grupo": "BR277_LITORAL", "quantidade_total": 2, "erro_medio": 8.5, "MAE": 8.5, "RMSE": 9.62, "p95": 13.0, "pct_dentro_15": 100.0}, {"grupo": "BR277_OESTE", "quantidade_total": 6, "erro_medio": -5.33, "MAE": 15.67, "RMSE": 20.26, "p95": 31.0, "pct_dentro_15": 50.0}, {"grupo": "CAMPOS_GERAIS", "quantidade_total": 3, "erro_medio": -18.0, "MAE": 18.0, "RMSE": 23.12, "p95": 38.0, "pct_dentro_15": 66.67}, {"grupo": "NOROESTE_INTERIOR", "quantidade_total": 2, "erro_medio": 17.0, "MAE": 17.0, "RMSE": 17.12, "p95": 19.0, "pct_dentro_15": 50.0}, {"grupo": "NORTE_CAFE", "quantidade_total": 4, "erro_medio": -16.5, "MAE": 18.0, "RMSE": 20.17, "p95": 27.0, "pct_dentro_15": 25.0}]
- Corredor fino: [{"grupo": "CAMPO_MOURAO", "quantidade_total": 1, "erro_medio": 15.0, "MAE": 15.0, "RMSE": 15.0, "p95": 15.0, "pct_dentro_15": 100.0}, {"grupo": "CASTRO", "quantidade_total": 1, "erro_medio": -12.0, "MAE": 12.0, "RMSE": 12.0, "p95": 12.0, "pct_dentro_15": 100.0}, {"grupo": "GUARATUBA", "quantidade_total": 1, "erro_medio": 4.0, "MAE": 4.0, "RMSE": 4.0, "p95": 4.0, "pct_dentro_15": 100.0}, {"grupo": "IRATI", "quantidade_total": 1, "erro_medio": -4.0, "MAE": 4.0, "RMSE": 4.0, "p95": 4.0, "pct_dentro_15": 100.0}, {"grupo": "JACAREZINHO", "quantidade_total": 2, "erro_medio": -25.0, "MAE": 25.0, "RMSE": 25.08, "p95": 27.0, "pct_dentro_15": 0.0}, {"grupo": "MATINHOS", "quantidade_total": 1, "erro_medio": 13.0, "MAE": 13.0, "RMSE": 13.0, "p95": 13.0, "pct_dentro_15": 100.0}, {"grupo": "PADRAO", "quantidade_total": 6, "erro_medio": -1.67, "MAE": 13.0, "RMSE": 17.44, "p95": 31.0, "pct_dentro_15": 50.0}, {"grupo": "PARANAVAI", "quantidade_total": 1, "erro_medio": 19.0, "MAE": 19.0, "RMSE": 19.0, "p95": 19.0, "pct_dentro_15": 0.0}, {"grupo": "PATO_BRANCO", "quantidade_total": 1, "erro_medio": -31.0, "MAE": 31.0, "RMSE": 31.0, "p95": 31.0, "pct_dentro_15": 0.0}, {"grupo": "TOLEDO", "quantidade_total": 1, "erro_medio": -7.0, "MAE": 7.0, "RMSE": 7.0, "p95": 7.0, "pct_dentro_15": 100.0}, {"grupo": "UNIAO_DA_VITORIA", "quantidade_total": 1, "erro_medio": -38.0, "MAE": 38.0, "RMSE": 38.0, "p95": 38.0, "pct_dentro_15": 0.0}]

# 7. OSRM vs fallback
- Route-aware por rota_fonte: [{"grupo": "OSRM", "quantidade_total": 17, "erro_medio": -5.94, "MAE": 15.94, "RMSE": 19.5, "p95": 38.0, "pct_dentro_15": 52.94}]
- Fallback por rota_fonte: [{"grupo": "ESTIMATIVA_LOCAL", "quantidade_total": 17, "erro_medio": 21.12, "MAE": 29.47, "RMSE": 39.31, "p95": 82.0, "pct_dentro_15": 41.18}]

# 8. Evidencias de generalizacao ou overfitting
- Houve generalizacao? False
- Houve indicio de overfitting? True
- Severidade: forte
- Qualidade fora da amostra: caiu_muito
- Modelo aceitavel fora da amostra? False

# 9. Problemas encontrados
- O cenario route-aware usou o demo publico do OSRM.

# 9.1 Dados nao confirmados
- Tempo de referencia e distancia de referencia das 17 rotas foram coletados manualmente em fonte unica (Rome2Rio) em 2026-03-11.
- Nenhuma rota desta etapa teve segunda confirmacao independente em outra fonte; os valores de referencia devem ser lidos como verdade operacional aproximada, nao ground truth oficial.

# 10. Recomendacao objetiva
- precisa recalibrar

# 11. Arquivos criados/usados
- C:\Users\tiago\OneDrive\Área de Trabalho\central de viagens 2.0\data\rotas_pr_validacao_cega.json
- C:\Users\tiago\OneDrive\Área de Trabalho\central de viagens 2.0\data\relatorio_validacao_cega.json
- C:\Users\tiago\OneDrive\Área de Trabalho\central de viagens 2.0\data\relatorio_validacao_cega.md
- C:\Users\tiago\OneDrive\Área de Trabalho\central de viagens 2.0\data\rotas_pr_benchmark.json