#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Coleta estruturada da estimativa local de viagem para rotas do Paraná.

Objetivos:
- Executar as mesmas rotas em dois cenários:
  1. Provider OSRM disponível
  2. Provider indisponível/simulado com falha
- Validar consistência dos campos antigos/novos
- Calcular métricas comparando o ETA do sistema com uma referência externa
- Medir impacto da degradação controlada

Uso:
  python scripts/benchmark_estimativa_pr_relatorio.py
  python scripts/benchmark_estimativa_pr_relatorio.py --refs-json data/rotas_pr_referencias_manual.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from copy import deepcopy
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.test.utils import override_settings

from eventos.services.estimativa_local import estimar_distancia_duracao

ROUTES = [
    {
        "origem": "Curitiba",
        "destino": "Pontal do Paraná",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -25.673533,
        "destino_lon": -48.511062,
    },
    {
        "origem": "Curitiba",
        "destino": "Ponta Grossa",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -25.091622,
        "destino_lon": -50.166787,
    },
    {
        "origem": "Curitiba",
        "destino": "Telêmaco Borba",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -24.324520,
        "destino_lon": -50.617585,
    },
    {
        "origem": "Curitiba",
        "destino": "Londrina",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -23.303975,
        "destino_lon": -51.169100,
    },
    {
        "origem": "Curitiba",
        "destino": "Maringá",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -23.420545,
        "destino_lon": -51.933298,
    },
    {
        "origem": "Curitiba",
        "destino": "Cianorte",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -23.659859,
        "destino_lon": -52.605444,
    },
    {
        "origem": "Curitiba",
        "destino": "Palotina",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -24.286784,
        "destino_lon": -53.840422,
    },
    {
        "origem": "Curitiba",
        "destino": "Cascavel",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -24.957301,
        "destino_lon": -53.459005,
    },
    {
        "origem": "Curitiba",
        "destino": "Foz do Iguaçu",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -25.542748,
        "destino_lon": -54.582689,
    },
    {
        "origem": "Curitiba",
        "destino": "Cruzeiro do Sul",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -22.962440,
        "destino_lon": -52.162210,
    },
    {
        "origem": "Curitiba",
        "destino": "Guarapuava",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -25.390237,
        "destino_lon": -51.462317,
    },
    {
        "origem": "Curitiba",
        "destino": "Paranaguá",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -25.516078,
        "destino_lon": -48.522528,
    },
    {
        "origem": "Curitiba",
        "destino": "Umuarama",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -23.765634,
        "destino_lon": -53.320110,
    },
    {
        "origem": "Curitiba",
        "destino": "Apucarana",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -23.549961,
        "destino_lon": -51.463486,
    },
    {
        "origem": "Curitiba",
        "destino": "Francisco Beltrão",
        "origem_lat": -25.419547,
        "origem_lon": -49.264622,
        "destino_lat": -26.081677,
        "destino_lon": -53.053466,
    },
]

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

DEFAULT_OSRM_URL = "https://router.project-osrm.org"
DEFAULT_FAILURE_URL = "http://127.0.0.1:5999"


def route_key(origem: str, destino: str) -> str:
    return f"{origem}::{destino}"


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * pct) - 1))
    return ordered[idx]


def safe_round(value: Any, ndigits: int = 1) -> float | None:
    if value is None:
        return None
    return round(float(value), ndigits)


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "quantize"):
        return float(value)
    return value


def clean_output(data: dict[str, Any]) -> dict[str, Any]:
    return {key: to_jsonable(value) for key, value in data.items()}


def missing_fields(data: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if field not in data]


def run_single_route(route: dict[str, Any]) -> dict[str, Any]:
    out = estimar_distancia_duracao(
        route["origem_lat"],
        route["origem_lon"],
        route["destino_lat"],
        route["destino_lon"],
    )
    out = clean_output(out)
    return {
        **deepcopy(route),
        "resultado": out,
        "missing_old_fields": missing_fields(out, OLD_FIELDS),
        "missing_new_fields": missing_fields(out, NEW_FIELDS),
        "duracao_bate_componentes": (
            out.get("duracao_estimada_min")
            == (out.get("tempo_viagem_estimado_min") or 0)
            + (out.get("buffer_operacional_sugerido_min") or 0)
        ),
    }


def run_scenario(
    *,
    name: str,
    osrm_enabled: bool,
    osrm_base_url: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    rows = []
    with override_settings(
        OSRM_ENABLED=osrm_enabled,
        OSRM_BASE_URL=osrm_base_url,
        OSRM_TIMEOUT_SECONDS=timeout_seconds,
    ):
        for route in ROUTES:
            rows.append(run_single_route(route))
    return {
        "scenario": name,
        "osrm_enabled": osrm_enabled,
        "osrm_base_url": osrm_base_url,
        "timeout_seconds": timeout_seconds,
        "rows": rows,
    }


def load_references(path: Path | None) -> dict[str, dict[str, Any]]:
    if not path or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    refs = {}
    for item in payload:
        refs[route_key(item["origem"], item["destino"])] = item
    return refs


def merge_references(rows: list[dict[str, Any]], refs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    merged = []
    for row in rows:
        item = deepcopy(row)
        ref = refs.get(route_key(row["origem"], row["destino"]), {})
        result = item["resultado"]
        ref_time = ref.get("tempo_referencia_min")
        ref_distance = ref.get("distancia_referencia_km")
        item["referencia"] = deepcopy(ref)
        if ref_time is not None:
            eta = result.get("tempo_viagem_estimado_min")
            total = result.get("duracao_estimada_min")
            item["erro_eta_min"] = None if eta is None else safe_round(eta - float(ref_time), 1)
            item["erro_eta_abs_min"] = None if eta is None else safe_round(abs(eta - float(ref_time)), 1)
            item["erro_total_min"] = None if total is None else safe_round(total - float(ref_time), 1)
            item["erro_total_abs_min"] = None if total is None else safe_round(abs(total - float(ref_time)), 1)
        else:
            item["erro_eta_min"] = None
            item["erro_eta_abs_min"] = None
            item["erro_total_min"] = None
            item["erro_total_abs_min"] = None
        if ref_distance is not None:
            dist = result.get("distancia_rodoviaria_km")
            item["erro_distancia_km"] = None if dist is None else safe_round(dist - float(ref_distance), 1)
            item["erro_distancia_abs_km"] = None if dist is None else safe_round(abs(dist - float(ref_distance)), 1)
        else:
            item["erro_distancia_km"] = None
            item["erro_distancia_abs_km"] = None
        merged.append(item)
    return merged


def metric_summary(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    if not values:
        return {
            "n": 0,
            "mae": None,
            "mediana": None,
            "p50": None,
            "p95": None,
            "p99": None,
            "pct_ate_5": None,
            "pct_ate_10": None,
            "pct_ate_15": None,
            "maior_erro_positivo": None,
            "maior_erro_negativo": None,
        }
    signed_key = key.replace("_abs_", "_")
    signed = [float(row[signed_key]) for row in rows if row.get(signed_key) is not None]
    n = len(values)
    return {
        "n": n,
        "mae": safe_round(sum(values) / n, 2),
        "mediana": safe_round(statistics.median(values), 2),
        "p50": safe_round(percentile(values, 0.50), 2),
        "p95": safe_round(percentile(values, 0.95), 2),
        "p99": safe_round(percentile(values, 0.99), 2),
        "pct_ate_5": safe_round(sum(1 for value in values if value <= 5) * 100 / n, 2),
        "pct_ate_10": safe_round(sum(1 for value in values if value <= 10) * 100 / n, 2),
        "pct_ate_15": safe_round(sum(1 for value in values if value <= 15) * 100 / n, 2),
        "maior_erro_positivo": safe_round(max(signed), 2) if signed else None,
        "maior_erro_negativo": safe_round(min(signed), 2) if signed else None,
    }


def grouped_summary(rows: list[dict[str, Any]], group_key: str, error_key: str, error_abs_key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result = row["resultado"]
        group_value = result.get(group_key) if group_key in result else row.get(group_key)
        group_value = group_value or "N/A"
        groups.setdefault(str(group_value), []).append(row)

    out = []
    for group_value, items in sorted(groups.items()):
        signed = [float(item[error_key]) for item in items if item.get(error_key) is not None]
        absolute = [float(item[error_abs_key]) for item in items if item.get(error_abs_key) is not None]
        out.append(
            {
                "grupo": group_value,
                "quantidade": len(items),
                "erro_medio": safe_round(sum(signed) / len(signed), 2) if signed else None,
                "erro_abs_medio": safe_round(sum(absolute) / len(absolute), 2) if absolute else None,
                "maior_erro": safe_round(max(signed, key=abs), 2) if signed else None,
            }
        )
    return out


def compare_scenarios(primary_rows: list[dict[str, Any]], degraded_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    degraded_index = {route_key(row["origem"], row["destino"]): row for row in degraded_rows}
    out = []
    for row in primary_rows:
        other = degraded_index[route_key(row["origem"], row["destino"])]
        a = row["resultado"]
        b = other["resultado"]
        out.append(
            {
                "origem": row["origem"],
                "destino": row["destino"],
                "distancia_osrm_km": a.get("distancia_rodoviaria_km"),
                "distancia_fallback_km": b.get("distancia_rodoviaria_km"),
                "delta_distancia_km": safe_round((b.get("distancia_rodoviaria_km") or 0) - (a.get("distancia_rodoviaria_km") or 0), 1),
                "eta_osrm_min": a.get("tempo_viagem_estimado_min"),
                "eta_fallback_min": b.get("tempo_viagem_estimado_min"),
                "delta_eta_min": safe_round((b.get("tempo_viagem_estimado_min") or 0) - (a.get("tempo_viagem_estimado_min") or 0), 1),
                "total_osrm_min": a.get("duracao_estimada_min"),
                "total_fallback_min": b.get("duracao_estimada_min"),
                "delta_total_min": safe_round((b.get("duracao_estimada_min") or 0) - (a.get("duracao_estimada_min") or 0), 1),
                "rota_fonte_osrm": a.get("rota_fonte"),
                "rota_fonte_fallback": b.get("rota_fonte"),
                "fallback_usado_osrm": a.get("fallback_usado"),
                "fallback_usado_fallback": b.get("fallback_usado"),
            }
        )
    return out


def field_presence_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    old_ok = all(not row["missing_old_fields"] for row in rows)
    new_ok = all(not row["missing_new_fields"] for row in rows)
    return {
        "old_fields_ok": old_ok,
        "new_fields_ok": new_ok,
        "rows_with_missing_old_fields": [
            {
                "origem": row["origem"],
                "destino": row["destino"],
                "missing_old_fields": row["missing_old_fields"],
            }
            for row in rows
            if row["missing_old_fields"]
        ],
        "rows_with_missing_new_fields": [
            {
                "origem": row["origem"],
                "destino": row["destino"],
                "missing_new_fields": row["missing_new_fields"],
            }
            for row in rows
            if row["missing_new_fields"]
        ],
        "duracao_bate_componentes_em_todos": all(row["duracao_bate_componentes"] for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark funcional da estimativa local PR")
    parser.add_argument("--refs-json", type=Path, default=None, help="JSON com referências externas por rota")
    parser.add_argument("--output-json", type=Path, default=BASE_DIR / "data" / "relatorio_estimativa_pr_coleta.json")
    parser.add_argument("--osrm-url", default=DEFAULT_OSRM_URL)
    parser.add_argument("--failure-url", default=DEFAULT_FAILURE_URL)
    parser.add_argument("--osrm-timeout", type=int, default=8)
    parser.add_argument("--failure-timeout", type=int, default=1)
    args = parser.parse_args()

    refs = load_references(args.refs_json)

    scenario_osrm = run_scenario(
        name="osrm_disponivel",
        osrm_enabled=True,
        osrm_base_url=args.osrm_url,
        timeout_seconds=args.osrm_timeout,
    )
    scenario_failure = run_scenario(
        name="osrm_indisponivel_falha_simulada",
        osrm_enabled=True,
        osrm_base_url=args.failure_url,
        timeout_seconds=args.failure_timeout,
    )

    primary_rows = merge_references(scenario_osrm["rows"], refs)
    degraded_rows = merge_references(scenario_failure["rows"], refs)

    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "references_loaded": len(refs),
        "scenario_osrm": {
            **{k: v for k, v in scenario_osrm.items() if k != "rows"},
            "field_presence": field_presence_summary(primary_rows),
            "rows": primary_rows,
            "metrics_eta": metric_summary(primary_rows, "erro_eta_abs_min"),
            "metrics_total": metric_summary(primary_rows, "erro_total_abs_min"),
            "by_corredor_macro": grouped_summary(primary_rows, "corredor_macro", "erro_eta_min", "erro_eta_abs_min"),
            "by_corredor_fino": grouped_summary(primary_rows, "corredor_fino", "erro_eta_min", "erro_eta_abs_min"),
            "by_rota_fonte": grouped_summary(primary_rows, "rota_fonte", "erro_eta_min", "erro_eta_abs_min"),
        },
        "scenario_fallback": {
            **{k: v for k, v in scenario_failure.items() if k != "rows"},
            "field_presence": field_presence_summary(degraded_rows),
            "rows": degraded_rows,
        },
        "degradation_compare": compare_scenarios(primary_rows, degraded_rows),
    }

    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    osrm_used = sum(
        1
        for row in primary_rows
        if row["resultado"].get("rota_fonte") == "OSRM" and row["resultado"].get("fallback_usado") is False
    )
    fallback_used = sum(
        1
        for row in degraded_rows
        if row["resultado"].get("rota_fonte") == "ESTIMATIVA_LOCAL" and row["resultado"].get("fallback_usado") is True
    )

    print(f"Rotas coletadas: {len(primary_rows)}")
    print(f"Referências externas carregadas: {len(refs)}")
    print(f"OSRM usado no cenário principal: {osrm_used}/{len(primary_rows)}")
    print(f"Fallback usado no cenário degradado: {fallback_used}/{len(degraded_rows)}")
    print(f"JSON salvo em: {args.output_json}")


if __name__ == "__main__":
    main()
