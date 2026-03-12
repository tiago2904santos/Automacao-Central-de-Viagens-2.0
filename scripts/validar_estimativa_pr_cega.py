#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validacao cega fora da amostra da estimativa de viagem do Parana."""
from __future__ import annotations

import argparse
import json
import math
import os
from datetime import UTC, datetime
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.test.utils import override_settings

from eventos.services.estimativa_local import estimar_distancia_duracao

VALIDATION_PATH = BASE_DIR / "data" / "rotas_pr_validacao_cega.json"
BENCHMARK_PATH = BASE_DIR / "data" / "rotas_pr_benchmark.json"
OUTPUT_JSON = BASE_DIR / "data" / "relatorio_validacao_cega.json"
OUTPUT_MD = BASE_DIR / "data" / "relatorio_validacao_cega.md"
DEFAULT_DEMO_OSRM_URL = "https://router.project-osrm.org"
DEFAULT_FAILURE_URL = "http://127.0.0.1:5999"

OLD_FIELDS = [
    "ok",
    "distancia_km",
    "tempo_cru_estimado_min",
    "tempo_adicional_sugerido_min",
    "duracao_estimada_min",
    "duracao_estimada_hhmm",
    "perfil_rota",
    "rota_fonte",
    "erro",
]
NEW_FIELDS = [
    "distancia_linha_reta_km",
    "distancia_rodoviaria_km",
    "velocidade_media_kmh",
    "corredor_macro",
    "corredor_fino",
    "rota_fonte",
    "fallback_usado",
    "confianca_estimativa",
    "refs_predominantes",
    "pedagio_presente",
    "travessia_urbana_presente",
    "serra_presente",
    "tempo_viagem_estimado_min",
    "tempo_viagem_estimado_hhmm",
    "buffer_operacional_sugerido_min",
]


def load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def route_key(record: dict[str, Any]) -> str:
    origem = record.get("origem_nome") or record.get("origem")
    destino = record.get("destino_nome") or record.get("destino")
    return f"{origem}::{destino}"


def safe_round(value: Any, ndigits: int = 2) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), ndigits)


def percentile(values: Iterable[float], pct: float) -> Optional[float]:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * pct) - 1))
    return ordered[index]


def resolve_route_aware_provider(args: argparse.Namespace) -> dict[str, Any]:
    configured_url = (getattr(settings, "OSRM_BASE_URL", "") or "").strip()
    configured_enabled = bool(getattr(settings, "OSRM_ENABLED", False) and configured_url)
    if args.osrm_url:
        return {"enabled": True, "base_url": args.osrm_url.strip(), "timeout": args.timeout, "source": "cli"}
    if configured_enabled:
        return {
            "enabled": True,
            "base_url": configured_url,
            "timeout": int(getattr(settings, "OSRM_TIMEOUT_SECONDS", args.timeout)),
            "source": "settings",
        }
    if not args.sem_demo_osrm:
        return {"enabled": True, "base_url": DEFAULT_DEMO_OSRM_URL, "timeout": args.timeout, "source": "demo"}
    return {"enabled": False, "base_url": "", "timeout": args.timeout, "source": "fallback_only"}


def estimate_row(record: dict[str, Any]) -> dict[str, Any]:
    out = estimar_distancia_duracao(
        record["origem_lat"],
        record["origem_lon"],
        record["destino_lat"],
        record["destino_lon"],
    )
    eta = out.get("tempo_viagem_estimado_min")
    buffer = out.get("buffer_operacional_sugerido_min")
    total = out.get("duracao_estimada_min")
    km_sys = out.get("distancia_rodoviaria_km")
    if km_sys is None:
        km_sys = out.get("distancia_km")
    row = {
        "origem": record["origem_nome"],
        "destino": record["destino_nome"],
        "km_ref": record.get("distancia_referencia_km"),
        "tempo_ref": record.get("tempo_referencia_min"),
        "fonte_ref": record.get("fonte_referencia"),
        "fonte_ref_link": record.get("fonte_link"),
        "data_coleta_ref": record.get("data_coleta"),
        "metodo_coleta_ref": record.get("metodo_coleta"),
        "cobertura_regional": record.get("cobertura_regional"),
        "ok": bool(out.get("ok")),
        "erro": out.get("erro"),
        "km_sys": safe_round(km_sys, 1),
        "ETA_tecnico_min": eta,
        "buffer_operacional_sugerido_min": buffer,
        "total_planejado_min": total,
        "corredor_macro": out.get("corredor_macro"),
        "corredor_fino": out.get("corredor_fino"),
        "refs_predominantes": out.get("refs_predominantes") or [],
        "rota_fonte": out.get("rota_fonte"),
        "fallback_usado": out.get("fallback_usado"),
        "confianca_estimativa": out.get("confianca_estimativa"),
        "duracao_bate_componentes": total == (eta or 0) + (buffer or 0),
        "eta_tecnico_separado_do_buffer": out.get("tempo_cru_estimado_min") == eta,
        "missing_old_fields": [field for field in OLD_FIELDS if field not in out],
        "missing_new_fields": [field for field in NEW_FIELDS if field not in out],
    }
    tempo_ref = record.get("tempo_referencia_min")
    if tempo_ref is not None and eta is not None:
        row["erro_ETA_min"] = safe_round(eta - float(tempo_ref), 1)
        row["erro_abs_ETA_min"] = safe_round(abs(eta - float(tempo_ref)), 1)
    else:
        row["erro_ETA_min"] = None
        row["erro_abs_ETA_min"] = None
    if tempo_ref is not None and total is not None:
        row["erro_total_min"] = safe_round(total - float(tempo_ref), 1)
        row["erro_abs_total_min"] = safe_round(abs(total - float(tempo_ref)), 1)
    else:
        row["erro_total_min"] = None
        row["erro_abs_total_min"] = None
    if record.get("distancia_referencia_km") is not None and row["km_sys"] is not None:
        row["erro_km"] = safe_round(row["km_sys"] - float(record["distancia_referencia_km"]), 1)
        row["erro_abs_km"] = safe_round(abs(row["km_sys"] - float(record["distancia_referencia_km"])), 1)
    else:
        row["erro_km"] = None
        row["erro_abs_km"] = None
    return row


def run_records(records: list[dict[str, Any]], provider: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with override_settings(
        OSRM_ENABLED=provider["enabled"],
        OSRM_BASE_URL=provider["base_url"],
        OSRM_TIMEOUT_SECONDS=provider["timeout"],
    ):
        for record in records:
            rows.append(estimate_row(record))
    return rows


def metric_summary(rows: list[dict[str, Any]], signed_key: str, abs_key: str) -> dict[str, Any]:
    absolute = [float(row[abs_key]) for row in rows if row.get(abs_key) is not None]
    signed = [float(row[signed_key]) for row in rows if row.get(signed_key) is not None]
    if not absolute:
        return {
            "quantidade_total": 0,
            "MAE": None,
            "RMSE": None,
            "mediana_erro_abs": None,
            "p50": None,
            "p95": None,
            "p99": None,
            "pct_dentro_5": None,
            "pct_dentro_10": None,
            "pct_dentro_15": None,
            "maior_erro_positivo": None,
            "maior_erro_negativo": None,
        }
    positive = max((row for row in rows if row.get(signed_key) is not None), key=lambda item: item[signed_key])
    negative = min((row for row in rows if row.get(signed_key) is not None), key=lambda item: item[signed_key])
    n = len(absolute)
    return {
        "quantidade_total": n,
        "MAE": safe_round(sum(absolute) / n, 2),
        "RMSE": safe_round(math.sqrt(sum(value * value for value in signed) / n), 2),
        "mediana_erro_abs": safe_round(percentile(absolute, 0.50), 2),
        "p50": safe_round(percentile(absolute, 0.50), 2),
        "p95": safe_round(percentile(absolute, 0.95), 2),
        "p99": safe_round(percentile(absolute, 0.99), 2),
        "pct_dentro_5": safe_round(sum(1 for value in absolute if value <= 5) * 100 / n, 2),
        "pct_dentro_10": safe_round(sum(1 for value in absolute if value <= 10) * 100 / n, 2),
        "pct_dentro_15": safe_round(sum(1 for value in absolute if value <= 15) * 100 / n, 2),
        "maior_erro_positivo": {
            "rota": f"{positive['origem']} -> {positive['destino']}",
            "erro_min": safe_round(positive[signed_key], 1),
        },
        "maior_erro_negativo": {
            "rota": f"{negative['origem']} -> {negative['destino']}",
            "erro_min": safe_round(negative[signed_key], 1),
        },
    }


def grouped_metrics(rows: list[dict[str, Any]], group_key: str) -> list[dict[str, Any]]:
    grouped: Dict[str, List[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get(group_key) or "N/A"), []).append(row)
    output: list[dict[str, Any]] = []
    for group_value in sorted(grouped):
        items = grouped[group_value]
        summary = metric_summary(items, "erro_ETA_min", "erro_abs_ETA_min")
        signed = [float(item["erro_ETA_min"]) for item in items if item.get("erro_ETA_min") is not None]
        output.append(
            {
                "grupo": group_value,
                "quantidade_total": len(items),
                "erro_medio": safe_round(sum(signed) / len(signed), 2) if signed else None,
                "MAE": summary["MAE"],
                "RMSE": summary["RMSE"],
                "p95": summary["p95"],
                "pct_dentro_15": summary["pct_dentro_15"],
            }
        )
    return output


def field_presence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "old_fields_ok": all(not row["missing_old_fields"] for row in rows),
        "new_fields_ok": all(not row["missing_new_fields"] for row in rows),
        "duracao_bate_componentes_em_todos": all(row["duracao_bate_componentes"] for row in rows),
        "ETA_separado_do_buffer_em_todos": all(row["eta_tecnico_separado_do_buffer"] for row in rows),
    }


def compare_scenarios(route_aware_rows: list[dict[str, Any]], fallback_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fallback_index = {f"{row['origem']}::{row['destino']}": row for row in fallback_rows}
    comparison: list[dict[str, Any]] = []
    for row in route_aware_rows:
        other = fallback_index[f"{row['origem']}::{row['destino']}"]
        comparison.append(
            {
                "origem": row["origem"],
                "destino": row["destino"],
                "km_ref": row["km_ref"],
                "tempo_ref": row["tempo_ref"],
                "ETA_osrm_min": row["ETA_tecnico_min"],
                "ETA_fallback_min": other["ETA_tecnico_min"],
                "buffer_osrm_min": row["buffer_operacional_sugerido_min"],
                "buffer_fallback_min": other["buffer_operacional_sugerido_min"],
                "total_osrm_min": row["total_planejado_min"],
                "total_fallback_min": other["total_planejado_min"],
                "erro_ETA_osrm_min": row["erro_ETA_min"],
                "erro_ETA_fallback_min": other["erro_ETA_min"],
                "corredor_macro_osrm": row["corredor_macro"],
                "corredor_fino_osrm": row["corredor_fino"],
                "refs_predominantes_osrm": row["refs_predominantes"],
                "rota_fonte_osrm": row["rota_fonte"],
                "rota_fonte_fallback": other["rota_fonte"],
                "fallback_usado_osrm": row["fallback_usado"],
                "fallback_usado_fallback": other["fallback_usado"],
                "confianca_osrm": row["confianca_estimativa"],
                "confianca_fallback": other["confianca_estimativa"],
            }
        )
    return comparison


def benchmark_summary(provider: dict[str, Any], benchmark_path: Path) -> dict[str, Any]:
    rows = run_records(load_json(benchmark_path), provider)
    return {
        "arquivo": str(benchmark_path),
        "quantidade_rotas": len(rows),
        "metrics_eta": metric_summary(rows, "erro_ETA_min", "erro_abs_ETA_min"),
    }


def compare_to_benchmark(benchmark_metrics: dict[str, Any], blind_metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "benchmark_calibrado": benchmark_metrics,
        "validacao_cega": blind_metrics,
        "delta_MAE": safe_round((blind_metrics.get("MAE") or 0) - (benchmark_metrics.get("MAE") or 0), 2),
        "delta_p95": safe_round((blind_metrics.get("p95") or 0) - (benchmark_metrics.get("p95") or 0), 2),
        "delta_pct_dentro_15": safe_round((blind_metrics.get("pct_dentro_15") or 0) - (benchmark_metrics.get("pct_dentro_15") or 0), 2),
        "ratio_MAE": safe_round((blind_metrics.get("MAE") or 0) / (benchmark_metrics.get("MAE") or 1), 2),
        "ratio_p95": safe_round((blind_metrics.get("p95") or 0) / (benchmark_metrics.get("p95") or 1), 2),
    }


def assess_generalization(comparison: dict[str, Any]) -> dict[str, Any]:
    blind = comparison["validacao_cega"]
    ratio_mae = comparison["ratio_MAE"] or 0
    delta_p95 = comparison["delta_p95"] or 0
    delta_pct15 = comparison["delta_pct_dentro_15"] or 0
    overfit = ratio_mae >= 1.75 or delta_p95 >= 8 or delta_pct15 <= -10
    severe = ratio_mae >= 2.5 or delta_p95 >= 15 or delta_pct15 <= -25
    if blind["MAE"] <= 10 and blind["p95"] <= 15 and blind["pct_dentro_15"] >= 85:
        recommendation = "aprovado para uso"
    elif blind["MAE"] <= 15 and blind["p95"] <= 25 and blind["pct_dentro_15"] >= 70:
        recommendation = "aprovado com ressalvas"
    else:
        recommendation = "precisa recalibrar"
    return {
        "houve_generalizacao": blind.get("pct_dentro_15") is not None and blind["pct_dentro_15"] >= 70,
        "houve_indicio_overfitting": overfit,
        "severidade_overfitting": "forte" if severe else "moderado" if overfit else "nenhum_indicio_relevante",
        "qualidade": "caiu_muito" if severe else "caiu_moderadamente" if overfit else "manteve_patamar",
        "modelo_aceitavel_fora_da_amostra": recommendation != "precisa recalibrar",
        "recomendacao_objetiva": recommendation,
        "observacao": (
            "A validacao cega ficou muito abaixo do benchmark calibrado."
            if severe
            else "A validacao cega degradou em relacao ao benchmark, mas sem colapso."
            if overfit
            else "A validacao cega permaneceu no mesmo patamar do benchmark calibrado."
        ),
    }


def scenario_payload(rows: list[dict[str, Any]], provider: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": provider,
        "field_presence": field_presence(rows),
        "rows": rows,
        "metrics_eta": metric_summary(rows, "erro_ETA_min", "erro_abs_ETA_min"),
        "metrics_total": metric_summary(rows, "erro_total_min", "erro_abs_total_min"),
        "by_corredor_macro": grouped_metrics(rows, "corredor_macro"),
        "by_corredor_fino": grouped_metrics(rows, "corredor_fino"),
        "by_rota_fonte": grouped_metrics(rows, "rota_fonte"),
    }


def build_markdown(report: dict[str, Any]) -> str:
    def metric_lines(title: str, metrics: dict[str, Any]) -> list[str]:
        return [
            f"**{title}**",
            "",
            f"- MAE: {metrics['MAE']} min",
            f"- RMSE: {metrics['RMSE']} min",
            f"- Mediana abs: {metrics['mediana_erro_abs']} min",
            f"- p50/p95/p99: {metrics['p50']} / {metrics['p95']} / {metrics['p99']} min",
            f"- <=5/10/15 min: {metrics['pct_dentro_5']}% / {metrics['pct_dentro_10']}% / {metrics['pct_dentro_15']}%",
            f"- Maior erro positivo: {metrics['maior_erro_positivo']['rota']} ({metrics['maior_erro_positivo']['erro_min']} min)",
            f"- Maior erro negativo: {metrics['maior_erro_negativo']['rota']} ({metrics['maior_erro_negativo']['erro_min']} min)",
        ]

    blind = report["scenario_route_aware"]["metrics_eta"]
    fallback = report["scenario_fallback"]["metrics_eta"]
    comp = report["comparacao_benchmark"]
    analysis = report["analise_generalizacao"]
    route_lines = ["| Rota | Regiao | Tempo ref | Km ref | Fonte | Coleta |", "| --- | --- | ---: | ---: | --- | --- |"]
    for row in report["validacao"]["rotas"]:
        route_lines.append(
            f"| {row['origem_nome']} -> {row['destino_nome']} | {row['cobertura_regional']} | {row['tempo_referencia_min']} | {row['distancia_referencia_km']:.1f} | [link]({row['fonte_link']}) | {row['metodo_coleta']} em {row['data_coleta']} |"
        )
    table_lines = [
        "| Destino | Km ref | T ref | ETA OSRM | Buf OSRM | Total OSRM | Erro ETA OSRM | ETA fallback | Buf fallback | Total fallback | Erro ETA fallback | Macro/Fino | Refs |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in report["comparacao_osrm_vs_fallback"]:
        refs = ", ".join(row["refs_predominantes_osrm"][:3]) if row["refs_predominantes_osrm"] else "-"
        macro_fino = f"{row['corredor_macro_osrm']}/{row['corredor_fino_osrm']}"
        table_lines.append(
            f"| {row['destino']} | {row['km_ref']:.1f} | {row['tempo_ref']} | {row['ETA_osrm_min']} | {row['buffer_osrm_min']} | {row['total_osrm_min']} | {row['erro_ETA_osrm_min']:+.1f} | {row['ETA_fallback_min']} | {row['buffer_fallback_min']} | {row['total_fallback_min']} | {row['erro_ETA_fallback_min']:+.1f} | {macro_fino} | {refs} |"
        )
    return "\n\n".join(
        [
            "# 1. Resumo executivo\n"
            f"- Rotas cegas: {report['validacao']['quantidade_rotas']}\n"
            f"- Provider route-aware: {report['scenario_route_aware']['provider']['source']} ({report['scenario_route_aware']['provider']['base_url'] or 'fallback'})\n"
            f"- Route-aware: MAE {blind['MAE']} min, p95 {blind['p95']} min, <=15 {blind['pct_dentro_15']}%\n"
            f"- Fallback: MAE {fallback['MAE']} min, p95 {fallback['p95']} min, <=15 {fallback['pct_dentro_15']}%\n"
            f"- Recomendacao: {analysis['recomendacao_objetiva']}\n"
            f"- Conclusao: {analysis['observacao']}",
            "# 2. Rotas da validacao cega\n" + "\n".join(route_lines),
            "# 3. Tabela completa dos resultados\n" + "\n".join(table_lines),
            "# 4. Metricas gerais\n" + "\n".join(metric_lines("Route-aware", blind) + [""] + metric_lines("Fallback", fallback)),
            "# 5. Comparacao com benchmark calibrado\n"
            f"- Benchmark calibrado MAE/p95/<=15: {comp['benchmark_calibrado']['MAE']} / {comp['benchmark_calibrado']['p95']} / {comp['benchmark_calibrado']['pct_dentro_15']}\n"
            f"- Validacao cega MAE/p95/<=15: {comp['validacao_cega']['MAE']} / {comp['validacao_cega']['p95']} / {comp['validacao_cega']['pct_dentro_15']}\n"
            f"- Delta MAE: {comp['delta_MAE']} min\n"
            f"- Delta p95: {comp['delta_p95']} min\n"
            f"- Delta <=15: {comp['delta_pct_dentro_15']} p.p.",
            "# 6. Analise por corredor\n"
            f"- Corredor macro: {json.dumps(report['scenario_route_aware']['by_corredor_macro'], ensure_ascii=False)}\n"
            f"- Corredor fino: {json.dumps(report['scenario_route_aware']['by_corredor_fino'], ensure_ascii=False)}",
            "# 7. OSRM vs fallback\n"
            f"- Route-aware por rota_fonte: {json.dumps(report['scenario_route_aware']['by_rota_fonte'], ensure_ascii=False)}\n"
            f"- Fallback por rota_fonte: {json.dumps(report['scenario_fallback']['by_rota_fonte'], ensure_ascii=False)}",
            "# 8. Evidencias de generalizacao ou overfitting\n"
            f"- Houve generalizacao? {analysis['houve_generalizacao']}\n"
            f"- Houve indicio de overfitting? {analysis['houve_indicio_overfitting']}\n"
            f"- Severidade: {analysis['severidade_overfitting']}\n"
            f"- Qualidade fora da amostra: {analysis['qualidade']}\n"
            f"- Modelo aceitavel fora da amostra? {analysis['modelo_aceitavel_fora_da_amostra']}",
            "# 9. Problemas encontrados\n" + "\n".join(f"- {item}" for item in report["problemas_encontrados"]),
            "# 9.1 Dados nao confirmados\n" + "\n".join(f"- {item}" for item in report["dados_nao_confirmados"]),
            "# 10. Recomendacao objetiva\n" + f"- {analysis['recomendacao_objetiva']}",
            "# 11. Arquivos criados/usados\n" + "\n".join(f"- {item}" for item in report["arquivos_criados_usados"]),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validacao cega da estimativa PR")
    parser.add_argument("--validation-file", type=Path, default=VALIDATION_PATH)
    parser.add_argument("--benchmark-file", type=Path, default=BENCHMARK_PATH)
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD)
    parser.add_argument("--osrm-url", default="")
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--sem-demo-osrm", action="store_true")
    parser.add_argument("--failure-url", default=DEFAULT_FAILURE_URL)
    parser.add_argument("--failure-timeout", type=int, default=1)
    args = parser.parse_args()

    validation_records = load_json(args.validation_file)
    benchmark_records = load_json(args.benchmark_file)
    if not validation_records:
        raise SystemExit(f"Nenhuma rota em {args.validation_file}.")

    overlaps = sorted(route_key(item) for item in validation_records if route_key(item) in {route_key(x) for x in benchmark_records})
    provider_route_aware = resolve_route_aware_provider(args)
    provider_fallback = {"enabled": True, "base_url": args.failure_url, "timeout": args.failure_timeout, "source": "forced_failure"}

    route_aware_rows = run_records(validation_records, provider_route_aware)
    fallback_rows = run_records(validation_records, provider_fallback)
    blind_metrics = metric_summary(route_aware_rows, "erro_ETA_min", "erro_abs_ETA_min")
    benchmark_metrics = benchmark_summary(provider_route_aware, args.benchmark_file)["metrics_eta"]
    comparison = compare_to_benchmark(benchmark_metrics, blind_metrics)
    analysis = assess_generalization(comparison)
    problems = []
    if overlaps:
        problems.append(f"Ha sobreposicao com o benchmark calibrado: {', '.join(overlaps)}")
    if provider_route_aware["source"] == "demo":
        problems.append("O cenario route-aware usou o demo publico do OSRM.")
    if not problems:
        problems.append("Nenhuma falha funcional detectada; a principal limitacao e a referencia externa ser de fonte unica e coleta manual.")
    unconfirmed = [
        "Tempo de referencia e distancia de referencia das 17 rotas foram coletados manualmente em fonte unica (Rome2Rio) em 2026-03-11.",
        "Nenhuma rota desta etapa teve segunda confirmacao independente em outra fonte; os valores de referencia devem ser lidos como verdade operacional aproximada, nao ground truth oficial.",
    ]

    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "validacao": {
            "arquivo": str(args.validation_file),
            "quantidade_rotas": len(validation_records),
            "fora_da_amostra_ok": not overlaps,
            "rotas_sobrepostas_com_benchmark": overlaps,
            "rotas": validation_records,
        },
        "scenario_route_aware": scenario_payload(route_aware_rows, provider_route_aware),
        "scenario_fallback": scenario_payload(fallback_rows, provider_fallback),
        "comparacao_osrm_vs_fallback": compare_scenarios(route_aware_rows, fallback_rows),
        "comparacao_benchmark": comparison,
        "analise_generalizacao": analysis,
        "problemas_encontrados": problems,
        "dados_nao_confirmados": unconfirmed,
        "arquivos_criados_usados": [
            str(args.validation_file),
            str(args.output_json),
            str(args.output_md),
            str(args.benchmark_file),
        ],
    }

    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    args.output_md.write_text(build_markdown(report), encoding="utf-8")

    print(f"Rotas cegas avaliadas: {len(validation_records)}")
    print(f"Fora da amostra: {'sim' if not overlaps else 'nao'}")
    print(f"Route-aware ETA: MAE={blind_metrics['MAE']} p95={blind_metrics['p95']} <=15={blind_metrics['pct_dentro_15']}%")
    print(f"Fallback ETA: MAE={report['scenario_fallback']['metrics_eta']['MAE']} p95={report['scenario_fallback']['metrics_eta']['p95']} <=15={report['scenario_fallback']['metrics_eta']['pct_dentro_15']}%")
    print(f"Relatorio JSON: {args.output_json}")
    print(f"Relatorio MD: {args.output_md}")


if __name__ == "__main__":
    main()
