# Estimativa PR

Arquivos principais:

- `eventos/services/estimativa_local.py`: orquestra ETA tecnico, calibracao e buffer.
- `eventos/services/corredores_pr.py`: classifica corredor macro/fino e atributos da rota.
- `eventos/services/routing_provider.py`: integra o provider route-aware (OSRM).
- `data/rotas_pr_benchmark.json`: benchmark oficial do Parana.
- `data/rotas_pr_calibracao.json`: calibracao aplicada ao ETA tecnico.
- `scripts/analisar_estimativa_pr.py`: mede benchmark e sugere ajustes.

Formula do ETA tecnico:

`eta_base_provider + ajuste_macro + ajuste_fino + ajuste_faixa + ajuste_atributos + ajuste_ref`

Garantia do contrato publico:

- `duracao_estimada_min = tempo_viagem_estimado_min + buffer_operacional_sugerido_min`
- campos antigos permanecem no retorno
- buffer operacional continua separado do ETA tecnico

Benchmark:

```powershell
python scripts/analisar_estimativa_pr.py
python scripts/analisar_estimativa_pr.py --sugerir-calibracao
```

Recalibracao:

1. Atualize `data/rotas_pr_benchmark.json` com novas rotas/referencias.
2. Rode `python scripts/analisar_estimativa_pr.py --sugerir-calibracao`.
3. Ajuste `data/rotas_pr_calibracao.json`.
4. Rode novamente o benchmark e os testes.

Observacoes importantes:

- `serra_presente` agora depende de corredor litoral/Serra do Mar ou geometria compativel, nao de qualquer `BR-277`.
- `corredor_fino` prioriza refs predominantes, geometria e municipio inferido por coordenadas.
- o benchmark oficial ja inclui as 15 rotas reais obrigatorias do Parana.
