#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark e calibracao da estimativa de viagem para o Parana.

Uso:
  python scripts/analisar_estimativa_pr.py
  python scripts/analisar_estimativa_pr.py --sugerir-calibracao
  python scripts/analisar_estimativa_pr.py --benchmark-file caminho.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
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

from eventos.services.estimativa_local import estimar_distancia_duracao, get_faixa_distancia_key

BENCHMARK_PATH = BASE_DIR / "data" / "rotas_pr_benchmark.json"
DEFAULT_DEMO_OSRM_URL = "https://router.project-osrm.org"
MAE_ALVO_MIN = 10
P95_ALVO_MIN = 15
PCT_DENTRO_15_ALVO = 85
MIN_AMOSTRAS_SUGESTAO = 2


def load_benchmark(path: Optional[Path] = None) -> list:
    benchmark_path = path or BENCHMARK_PATH
    if not benchmark_path.exists():
        return []
    return json.loads(benchmark_path.read_text(encoding="utf-8"))


def tempo_referencia(record: dict) -> Optional[float]:
    value = record.get("tempo_referencia_min")
    if value is not None:
        return float(value)
    value = record.get("tempo_google_min")
    if value is not None:
        return float(value)
    return None


def distancia_referencia(record: dict) -> Optional[float]:
    value = record.get("distancia_referencia_km")
    if value is not None:
        return float(value)
    value = record.get("distancia_google_km")
    if value is not None:
        return float(value)
    return None


def _percentile(values: Iterable[float], pct: float) -> Optional[float]:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * pct) - 1))
    return ordered[index]


def _resolve_provider(
    benchmark_file: Optional[Path],
    force_demo_osrm: bool,
    disable_demo_osrm: bool,
    osrm_url: Optional[str],
    timeout_seconds: int,
) -> Dict[str, Any]:
    configured_url = (getattr(settings, "OSRM_BASE_URL", "") or "").strip()
    configured_enabled = bool(getattr(settings, "OSRM_ENABLED", False) and configured_url)
    is_default_benchmark = (benchmark_file or BENCHMARK_PATH).resolve() == BENCHMARK_PATH.resolve()

    if osrm_url:
        return {"enabled": True, "base_url": osrm_url.strip(), "timeout": timeout_seconds, "source": "cli"}
    if configured_enabled:
        return {
            "enabled": True,
            "base_url": configured_url,
            "timeout": getattr(settings, "OSRM_TIMEOUT_SECONDS", timeout_seconds),
            "source": "settings",
        }
    if force_demo_osrm or (is_default_benchmark and not disable_demo_osrm):
        return {"enabled": True, "base_url": DEFAULT_DEMO_OSRM_URL, "timeout": timeout_seconds, "source": "demo"}
    return {"enabled": False, "base_url": "", "timeout": timeout_seconds, "source": "fallback"}


def run_estimator(record: dict) -> Optional[dict]:
    origem_lat = record.get("origem_lat")
    origem_lon = record.get("origem_lon")
    destino_lat = record.get("destino_lat")
    destino_lon = record.get("destino_lon")
    if None in (origem_lat, origem_lon, destino_lat, destino_lon):
        return None
    out = estimar_distancia_duracao(origem_lat, origem_lon, destino_lat, destino_lon)
    if not out.get("ok"):
        return None
    distancia_km = out.get("distancia_rodoviaria_km")
    if distancia_km is None:
        distancia_km = float(out.get("distancia_km") or 0)
    refs = out.get("refs_predominantes") or []
    return {
        "distancia_estimador_km": float(distancia_km),
        "tempo_estimador_min": out.get("tempo_viagem_estimado_min"),
        "buffer_operacional_min": out.get("buffer_operacional_sugerido_min"),
        "duracao_total_min": out.get("duracao_estimada_min"),
        "corredor_macro": out.get("corredor_macro"),
        "corredor_fino": out.get("corredor_fino"),
        "rota_fonte": out.get("rota_fonte"),
        "fallback_usado": out.get("fallback_usado"),
        "faixa_distancia": get_faixa_distancia_key(float(distancia_km)),
        "ref_predominante": refs[0] if refs else None,
        "refs_predominantes": refs,
        "serra_presente": out.get("serra_presente"),
        "pedagio_presente": out.get("pedagio_presente"),
        "travessia_urbana_presente": out.get("travessia_urbana_presente"),
    }


def _group_signed(rows: List[dict], key: str) -> Dict[str, List[float]]:
    groups: Dict[str, List[float]] = {}
    for row in rows:
        group_value = row.get(key) or "N/A"
        groups.setdefault(str(group_value), []).append(float(row["erro_min"]))
    return groups


def _print_group_metrics(rows: List[dict], key: str, label: str) -> None:
    groups_abs: Dict[str, List[float]] = {}
    groups_signed: Dict[str, List[float]] = {}
    for row in rows:
        group_value = str(row.get(key) or "N/A")
        groups_abs.setdefault(group_value, []).append(float(row["erro_abs_min"]))
        groups_signed.setdefault(group_value, []).append(float(row["erro_min"]))
    print(f"\n--- Erro por {label} ---")
    for group_value in sorted(groups_abs):
        absolute = groups_abs[group_value]
        signed = groups_signed[group_value]
        mae = sum(absolute) / len(absolute)
        erro_medio = sum(signed) / len(signed)
        print(f"  {group_value}: n={len(absolute)} erro_medio={erro_medio:.1f} mae={mae:.1f}")


def _emitir_maiores_erros(rows: List[dict]) -> None:
    maior_positivo = max(rows, key=lambda row: row["erro_min"])
    maior_negativo = min(rows, key=lambda row: row["erro_min"])

    def route_label(row: dict) -> str:
        origem = row.get("origem_nome") or f"({row.get('origem_lat')}, {row.get('origem_lon')})"
        destino = row.get("destino_nome") or f"({row.get('destino_lat')}, {row.get('destino_lon')})"
        return f"{origem} -> {destino}"

    print("\n--- Extremes ---")
    print(
        "  Maior erro positivo: "
        f"{route_label(maior_positivo)} = {maior_positivo['erro_min']:.1f} min "
        f"({maior_positivo['corredor_macro']}/{maior_positivo['corredor_fino']})"
    )
    print(
        "  Maior erro negativo: "
        f"{route_label(maior_negativo)} = {maior_negativo['erro_min']:.1f} min "
        f"({maior_negativo['corredor_macro']}/{maior_negativo['corredor_fino']})"
    )


def _emitir_mismatches_classificacao(rows: List[dict]) -> None:
    mismatches_macro = [
        row for row in rows
        if row.get("corredor_macro_esperado") and row.get("corredor_macro") != row.get("corredor_macro_esperado")
    ]
    mismatches_fino = [
        row for row in rows
        if row.get("corredor_fino_esperado") and row.get("corredor_fino") != row.get("corredor_fino_esperado")
    ]
    print("\n--- Classificacao ---")
    print(f"  Macro correto: {len(rows) - len(mismatches_macro)}/{len(rows)}")
    print(f"  Fino correto: {len(rows) - len(mismatches_fino)}/{len(rows)}")
    if mismatches_macro[:5]:
        for row in mismatches_macro[:5]:
            print(
                f"  Macro mismatch: {row['origem_nome']} -> {row['destino_nome']} "
                f"esperado={row['corredor_macro_esperado']} atual={row['corredor_macro']}"
            )
    if mismatches_fino[:5]:
        for row in mismatches_fino[:5]:
            print(
                f"  Fino mismatch: {row['origem_nome']} -> {row['destino_nome']} "
                f"esperado={row['corredor_fino_esperado']} atual={row['corredor_fino']}"
            )


def _emitir_sugestoes_calibracao(rows: List[dict]) -> None:
    print("\n=== Sugestoes de calibracao ===")

    def suggest(title: str, key: str) -> None:
        groups = _group_signed(rows, key)
        print(f"\n{title}:")
        for group_value in sorted(groups):
            values = groups[group_value]
            if len(values) < MIN_AMOSTRAS_SUGESTAO:
                continue
            erro_medio = sum(values) / len(values)
            sugestao = -int(round(erro_medio))
            print(f"  '{group_value}': {sugestao},")

    suggest("AJUSTE_CORREDOR_MACRO_MIN", "corredor_macro")
    suggest("AJUSTE_CORREDOR_FINO_MIN", "corredor_fino")
    suggest("AJUSTE_FAIXA_DISTANCIA_MIN", "faixa_distancia")
    suggest("AJUSTE_REF_PREDOMINANTE_MIN", "ref_predominante")
    print("\nUse as sugestoes como ponto de partida em data/rotas_pr_calibracao.json.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark da estimativa PR")
    parser.add_argument("--benchmark-file", type=Path, default=None, help="JSON de benchmark (default: data/rotas_pr_benchmark.json)")
    parser.add_argument("--sugerir-calibracao", action="store_true", help="Emite sugestoes agregadas por grupo")
    parser.add_argument("--osrm-url", default="", help="Forca um OSRM para o benchmark")
    parser.add_argument("--timeout", type=int, default=8, help="Timeout do provider do benchmark")
    parser.add_argument("--usar-demo-osrm", action="store_true", help="Usa router.project-osrm.org quando settings nao estiver configurado")
    parser.add_argument("--sem-demo-osrm", action="store_true", help="Nao usa demo publico; mantem fallback puro")
    args = parser.parse_args()

    benchmark_records = load_benchmark(args.benchmark_file)
    if not benchmark_records:
        print(f"Nenhum registro em {(args.benchmark_file or BENCHMARK_PATH)}.")
        return

    provider_cfg = _resolve_provider(
        args.benchmark_file,
        force_demo_osrm=args.usar_demo_osrm,
        disable_demo_osrm=args.sem_demo_osrm,
        osrm_url=args.osrm_url,
        timeout_seconds=args.timeout,
    )

    rows: List[dict] = []
    with override_settings(
        OSRM_ENABLED=provider_cfg["enabled"],
        OSRM_BASE_URL=provider_cfg["base_url"],
        OSRM_TIMEOUT_SECONDS=provider_cfg["timeout"],
    ):
        for record in benchmark_records:
            estimated = run_estimator(record)
            if estimated is None:
                continue
            row = {**record, **estimated}
            tempo_ref = tempo_referencia(record)
            distancia_ref = distancia_referencia(record)
            if tempo_ref is not None:
                row["tempo_referencia_min"] = tempo_ref
                row["erro_min"] = float((estimated.get("tempo_estimador_min") or 0) - tempo_ref)
                row["erro_abs_min"] = abs(row["erro_min"])
            if distancia_ref is not None:
                row["erro_distancia_km"] = float((estimated.get("distancia_estimador_km") or 0) - distancia_ref)
                row["erro_abs_distancia_km"] = abs(row["erro_distancia_km"])
            rows.append(row)

    total_registros = len(benchmark_records)
    total_estimados = len(rows)
    rows_com_ref = [row for row in rows if "erro_abs_min" in row]
    print("=== Benchmark estimativa PR ===")
    print(f"Arquivo benchmark: {args.benchmark_file or BENCHMARK_PATH}")
    print(f"Provider benchmark: {provider_cfg['source']} ({provider_cfg['base_url'] or 'fallback'})")
    print(f"Registros no arquivo: {total_registros}")
    print(f"Registros com estimativa: {total_estimados}")
    print(f"Registros com referencia temporal: {len(rows_com_ref)}")

    if not rows_com_ref:
        print("\nPreencha tempo_referencia_min para calcular metricas.")
        return

    erros_abs = [float(row["erro_abs_min"]) for row in rows_com_ref]
    erros_signed = [float(row["erro_min"]) for row in rows_com_ref]
    mae = sum(erros_abs) / len(erros_abs)
    rmse = math.sqrt(sum(value * value for value in erros_signed) / len(erros_signed))
    mediana = _percentile(erros_abs, 0.50)
    p50 = _percentile(erros_abs, 0.50)
    p95 = _percentile(erros_abs, 0.95)
    p99 = _percentile(erros_abs, 0.99)
    dentro_5 = sum(1 for value in erros_abs if value <= 5) * 100 / len(erros_abs)
    dentro_10 = sum(1 for value in erros_abs if value <= 10) * 100 / len(erros_abs)
    dentro_15 = sum(1 for value in erros_abs if value <= 15) * 100 / len(erros_abs)

    print("\n--- Metricas ---")
    print(f"MAE: {mae:.1f} min (alvo <= {MAE_ALVO_MIN})")
    print(f"RMSE: {rmse:.1f} min")
    print(f"Mediana erro abs: {mediana:.1f} min")
    print(f"p50: {p50:.1f} min")
    print(f"p95: {p95:.1f} min (alvo <= {P95_ALVO_MIN})")
    print(f"p99: {p99:.1f} min")
    print(f"% dentro de 5 min: {dentro_5:.1f}%")
    print(f"% dentro de 10 min: {dentro_10:.1f}%")
    print(f"% dentro de 15 min: {dentro_15:.1f}% (alvo >= {PCT_DENTRO_15_ALVO})")

    _emitir_mismatches_classificacao(rows)
    _print_group_metrics(rows_com_ref, "corredor_macro", "corredor macro")
    _print_group_metrics(rows_com_ref, "corredor_fino", "corredor fino")
    _print_group_metrics(rows_com_ref, "faixa_distancia", "faixa de distancia")
    _print_group_metrics(rows_com_ref, "rota_fonte", "provider")
    _emitir_maiores_erros(rows_com_ref)

    if args.sugerir_calibracao:
        _emitir_sugestoes_calibracao(rows_com_ref)


if __name__ == "__main__":
    main()
