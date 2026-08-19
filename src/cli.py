"""Headless CLI for the NOM-HRMS-FGA pipeline (no tkinter).

Usage::

    nom-hrms-fga-cli --input file.csv --preset soil --output result.csv
    nom-hrms-fga-cli --input file.csv --ppm-tol 3.0 --isotope-filter

Result CSV goes to ``--output`` (or stdout); progress goes to stderr.
Exit code 0 on success, 1 on error.
"""

from __future__ import annotations

import argparse
import sys
from contextlib import redirect_stdout

from src.configs.presets_loader import load_preset

#: Preset keys passed through to ``run_pipeline`` unchanged.
_PRESET_DIRECT_KEYS = (
    "load_mass_min",
    "load_mass_max",
    "noise_force",
    "noise_intensity",
    "noise_quantile",
    "rel_error",
    "ppm_tol",
    "max_groups",
    "allow_gaps",
    "sign",
)


def _preset_to_kwargs(params: dict) -> dict:
    kwargs: dict = {}
    for key in _PRESET_DIRECT_KEYS:
        if key in params:
            kwargs[key] = params[key]
    if "element_ranges" in params:
        kwargs["brutto_dict"] = {
            el: tuple(rng) for el, rng in params["element_ranges"].items()
        }
    return kwargs


def _parse_element_ranges(spec: str) -> dict:
    """Parse ``'C:5-60,H:4-120,O:1-30,N:0-3'`` → ``{'C': (5, 60), ...}``."""
    brutto: dict = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        el, _, rng = part.partition(":")
        lo, _, hi = rng.partition("-")
        brutto[el.strip()] = (int(lo), int(hi))
    return brutto


def _resolve_input(path: str) -> str:
    """Resolve RAW / mzML input to an averaged JSON table; CSV/XLSX as-is."""
    lower = path.lower()
    if lower.endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0)
    if lower.endswith(".mzml"):
        from src.core.io.mzml_bridge import mzml_to_json

        return mzml_to_json(path, rt_min=0.0, rt_max=999.0)
    return path


def _build_parser() -> argparse.ArgumentParser:
    from src import __version__

    p = argparse.ArgumentParser(
        prog="nom-hrms-fga-cli",
        description="NOM-HRMS-FGA: анализ -COOH/-OH групп (headless, без GUI).",
    )
    p.add_argument(
        "--input",
        "-i",
        required=True,
        help="исходный спектр (.csv/.xlsx/.json/.raw/.mzML)",
    )
    p.add_argument("--dmet", help="дейтерометилированный спектр")
    p.add_argument("--dacet", help="дейтероацилированный спектр")
    p.add_argument(
        "--preset",
        choices=["soil", "water", "peat", "coal"],
        help="пресет параметров",
    )
    p.add_argument(
        "--output",
        "-o",
        help="выходной файл результата (.csv/.xlsx/.json); по умолчанию CSV в stdout",
    )
    p.add_argument("--sep", help="разделитель входного CSV")
    p.add_argument("--mass-min", type=float, dest="load_mass_min")
    p.add_argument("--mass-max", type=float, dest="load_mass_max")
    p.add_argument("--noise-force", type=float)
    p.add_argument("--noise-intensity", type=float)
    p.add_argument("--noise-quantile", type=float)
    p.add_argument("--rel-error", type=float)
    p.add_argument("--sign")
    p.add_argument("--ppm-tol", type=float)
    p.add_argument("--max-groups", type=int)
    p.add_argument("--allow-gaps", action="store_true", default=None)
    p.add_argument("--isotope-filter", action="store_true", default=None)
    p.add_argument(
        "--element-ranges",
        help="диапазоны элементов, напр. 'C:5-60,H:4-120,O:1-30,N:0-3'",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # ── 1. Собираем параметры: пресет → явные флаги ────────────────────────────
    kwargs: dict = {}
    if args.preset:
        preset = load_preset(args.preset)
        if preset is None:
            print(f"Ошибка: пресет '{args.preset}' не найден", file=sys.stderr)
            return 1
        kwargs.update(_preset_to_kwargs(preset.get("params", {})))

    for key in _PRESET_DIRECT_KEYS:
        val = getattr(args, key, None)
        if val is not None:
            kwargs[key] = val
    if args.sep is not None:
        kwargs["sep"] = args.sep
    if args.allow_gaps is not None:
        kwargs["allow_gaps"] = args.allow_gaps
    if args.isotope_filter is not None:
        kwargs["isotope_filter"] = args.isotope_filter
    if args.element_ranges:
        kwargs["brutto_dict"] = _parse_element_ranges(args.element_ranges)

    # ── 2. Разрешаем входы (RAW / mzML → JSON) ────────────────────────────────
    try:
        src_path = _resolve_input(args.input)
        dmet_path = _resolve_input(args.dmet) if args.dmet else None
        dacet_path = _resolve_input(args.dacet) if args.dacet else None
    except Exception as e:
        print(f"Ошибка загрузки входных данных: {e}", file=sys.stderr)
        return 1

    # ── 3. Запуск пайплайна (прогресс → stderr) ───────────────────────────────
    from src.core import run_pipeline

    try:
        with redirect_stdout(sys.stderr):
            res = run_pipeline(
                src_path=src_path,
                dmet_path=dmet_path,
                dacet_path=dacet_path,
                visualize=False,
                **kwargs,
            )
    except Exception as e:
        print(f"Ошибка выполнения: {e}", file=sys.stderr)
        return 1

    # Пайплайн мог вернуть пустой результат с сообщениями об ошибках
    # (например, отсутствующие файлы) — для CLI это тоже ошибка.
    if getattr(res, "messages", None):
        return 1

    # ── 4. Вывод результата ────────────────────────────────────────────────────
    try:
        if args.output:
            from src.core.pipeline._export import export_result_table

            export_result_table(res.table, args.output)
        else:
            res.table.to_csv(sys.stdout, index=False, sep=";")
    except Exception as e:
        print(f"Ошибка записи результата: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
