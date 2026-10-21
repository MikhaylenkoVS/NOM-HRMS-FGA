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
from src.core.console import ensure_utf8_stdio

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


def _halogen_warning(kwargs: dict) -> str | None:
    """Предупреждение о числе галогенных комбинаций и замедлении (до анализа)."""
    try:
        from src.configs import FORMULA_SEARCH_CFG
        from src.core.spectrum._constants import FormulaSearchConfig
        from src.core.spectrum._formula_source import halogen_search_plan

        cfg = FormulaSearchConfig()
        ranges = dict(cfg.ranges or {})
        brutto = kwargs.get("brutto_dict")
        if brutto:
            for el, rng in brutto.items():
                ranges[el] = (int(rng[0]), int(rng[1]))
        cfg.ranges = ranges

        hs = getattr(FORMULA_SEARCH_CFG, "halogen_search", None) or {}
        plan = halogen_search_plan(
            cfg,
            max_combinations=int(
                kwargs.get("halogen_max_combinations", hs.get("max_combinations", 16))
            ),
            exhaustive=bool(
                kwargs.get("halogen_exhaustive", hs.get("exhaustive", True))
            ),
            max_atoms_total=int(kwargs.get("halogen_max_atoms", 5)),
        )
    except Exception:
        return None
    # Предупреждение показывается только при включённом флаге конфига
    # (halogen_search.show_warning); код оставлен для будущего использования.
    if not (plan.get("warn") and plan.get("warn_enabled")):
        return None
    limits = plan.get("limits", {})
    window = (
        ", ".join(
            f"{el}<={limits[el]}" for el in ("F", "Cl", "Br", "I") if limits.get(el)
        )
        or "галогены выключены"
    )
    return (
        "[ВНИМАНИЕ] Проверка комбинаций галогенов: "
        f"{plan['selected']} из {plan['allowed']} допустимых (окна: {window}).\n"
        "           Ориентировочное замедление назначения формул: "
        f"x{plan['slowdown']:.2f} (база — 16 комбинаций; замерено на "
        "set_01/set_02).\n"
        "           Уменьшить: --halogen-max-combinations N, "
        "--no-halogen-exhaustive или сузить окна через --element-ranges.\n"
        "           В GUI то же настраивается в окне "
        "«Настройки поиска по галогенам…» (вкладка «Параметры», блок «Фильтры»)."
    )


def _parse_element_ranges(spec: str) -> dict:
    """Parse ``'C:5-60,H:4-120,O:1-30,N:0-3'`` → ``{'C': (5, 60), ...}``.

    Raises
    ------
    ValueError
        Если элемент не соответствует виду ``El:min-max``, границы не целые
        или нижняя граница больше верхней. Текст исключения пригоден для
        показа пользователю.
    """
    brutto: dict = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        el, colon, rng = part.partition(":")
        if not colon:
            raise ValueError(f"ожидается 'C:5-60', получено '{part}'")
        lo_s, dash, hi_s = rng.partition("-")
        if not dash:
            raise ValueError(f"ожидается 'C:5-60', получено '{part}'")
        try:
            lo, hi = int(lo_s), int(hi_s)
        except ValueError:
            raise ValueError(f"границы должны быть целыми: '{part}'") from None
        if lo > hi:
            raise ValueError(f"нижняя граница больше верхней: '{part}'")
        brutto[el.strip()] = (lo, hi)
    if not brutto:
        raise ValueError("не задано ни одного элемента")
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
    p.add_argument(
        "--profile-check",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="проверять профиль интенсивностей продуктов (по умолчанию выключено)",
    )
    p.add_argument(
        "--profile-max-jump",
        type=float,
        default=None,
        help="максимальное отношение I(n+1)/I(n) между ступенями (0 — не проверять)",
    )
    p.add_argument(
        "--profile-max-corr",
        type=float,
        default=None,
        help="максимальная корреляция «номер ступени — интенсивность»",
    )
    p.add_argument(
        "--series-anchor",
        choices=["theoretical", "observed"],
        default=None,
        help="от чего считать сдвиг ступеней: от теоретической массы брутто "
        "(theoretical) или от наблюдаемого пика того же соединения в "
        "производном спектре (observed)",
    )
    p.add_argument(
        "--anchor-ppm",
        type=float,
        default=None,
        help="окно поиска якорного пика для series-anchor=observed, ppm",
    )
    p.add_argument(
        "--significance-level",
        type=float,
        default=None,
        help="уровень доверия для длины серии (0.95 → p<0.05; чем выше, тем строже)",
    )
    p.add_argument(
        "--require-first-step",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="требовать подтверждённую первую ступень серии (по умолчанию выключено; "
        "--require-first-step — включить)",
    )
    p.add_argument(
        "--max-gaps",
        type=int,
        default=None,
        help="допустимое число пропущенных ступеней внутри серии "
        "(по умолчанию 0 — без пропусков)",
    )
    p.add_argument(
        "--allow-gaps",
        action="store_true",
        default=None,
        help="устаревший синоним: разрешить пропуски (число по умолчанию — 1)",
    )
    p.add_argument(
        "--no-allow-gaps",
        dest="allow_gaps",
        action="store_false",
        default=None,
        help="устаревший синоним: запретить пропуски (то же, что --max-gaps 0)",
    )
    p.add_argument(
        "--db-variants",
        action="store_true",
        help="показать варианты базы формул (объём, ускорение, что установлено) и выйти",
    )
    p.add_argument(
        "--halogen-exhaustive",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "проверять ВСЕ комбинации галогенов в заданных окнах элементов "
            "(по умолчанию проверяются только самые приоритетные — "
            "значительно быстрее)"
        ),
    )
    p.add_argument(
        "--halogen-max-combinations",
        type=int,
        default=None,
        metavar="N",
        help=(
            "сколько комбинаций галогенов проверять в обычном режиме "
            "(по умолчанию 16; комбинации выбираются по приоритету)"
        ),
    )
    p.add_argument(
        "--denoise-source",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "шумоподавление исходного спектра (по умолчанию включено; "
            "--no-denoise-source — если пиклист уже отфильтрован)"
        ),
    )
    p.add_argument(
        "--denoise-derivatives",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "шумоподавление спектров дериватизатов (по умолчанию выключено: "
            "пики продуктов низкоинтенсивные)"
        ),
    )
    p.add_argument(
        "--max-xc",
        type=float,
        default=None,
        help=(
            "жёсткий фильтр (F+Cl+Br+I)/C, напр. 0.1; по умолчанию выключен "
            "(фильтр — пользовательская настройка)"
        ),
    )
    p.add_argument(
        "--halogen-max-atoms",
        type=int,
        default=None,
        help="предел числа атомов галогенов в брутто-формуле (по умолчанию 5)",
    )
    p.add_argument(
        "--isotope-filter",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "изотопный фильтр M+1/M+2 (включён по умолчанию; "
            "--no-isotope-filter выключает)"
        ),
    )
    p.add_argument(
        "--isotope-variants",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "искать изотопные варианты (13C, 34S, 37Cl, 81Br, …) для найденных "
            "формул и помечать пики-сателлиты (включено по умолчанию; "
            "--no-isotope-variants выключает)"
        ),
    )
    p.add_argument(
        "--element-ranges",
        help=(
            "диапазоны элементов, напр. 'C:5-60,H:4-120,O:1-30,N:0-3' "
            "или с галогенами 'C:5-60,H:4-120,O:1-30,N:0-3,S:0-2,Cl:0-1'; "
            "не указанные элементы берутся из formula_search.json"
        ),
    )
    p.add_argument(
        "--segment-width",
        type=float,
        help="ширина RT-отрезка (мин); включает сегментный режим усреднения",
    )
    p.add_argument(
        "--rt-min",
        type=float,
        default=0.0,
        help="начало RT-диапазона (мин) для сегментного режима (по умолчанию 0)",
    )
    p.add_argument(
        "--rt-max",
        type=float,
        default=20.0,
        help="конец RT-диапазона (мин) для сегментного режима (по умолчанию 20)",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None) -> int:
    # Русский текст в сообщениях + перенаправленный stdout на Windows
    # (ANSI-кодировка) иначе приводят к UnicodeEncodeError.
    ensure_utf8_stdio()

    # --db-variants отвечает до разбора остальных аргументов: --input для него
    # не нужен (пользователь может просто посмотреть варианты баз).
    if argv is None:
        argv = sys.argv[1:]
    if "--db-variants" in argv:
        from src.core.formula_db._variants import (
            describe_choice,
            installer_plan,
            variants_report,
        )

        print(f"{'вариант':36s} {'объём':>9s} {'ускорение':>11s}  установлен")
        for row in variants_report():
            mark = "да" if row["installed"] else "нет"
            print(
                f"{row['title']:36s} {row['size_mb']:8.1f}М "
                f"{row['speedup']:>11s}  {mark}"
            )
        plan = installer_plan()
        print(f"\nинсталлер: {plan['summary']}")
        print(f"будет использовано: {describe_choice()}")
        return 0

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
    if args.max_gaps is not None:
        kwargs["max_gaps"] = args.max_gaps
    if args.require_first_step is not None:
        kwargs["require_first_step"] = args.require_first_step
    if args.significance_level is not None:
        kwargs["significance_level"] = args.significance_level
    if args.series_anchor is not None:
        kwargs["series_anchor"] = args.series_anchor
    if args.profile_check is not None:
        kwargs["profile_check"] = args.profile_check
    if args.profile_max_jump is not None:
        kwargs["profile_max_jump"] = args.profile_max_jump or None
    if args.profile_max_corr is not None:
        kwargs["profile_max_corr"] = args.profile_max_corr
    if args.anchor_ppm is not None:
        kwargs["anchor_ppm"] = args.anchor_ppm
    if args.allow_gaps is not None:
        kwargs["allow_gaps"] = args.allow_gaps
    if args.isotope_filter is not None:
        kwargs["isotope_filter"] = args.isotope_filter
    if args.isotope_variants is not None:
        kwargs["isotope_variants"] = args.isotope_variants
    if args.max_xc is not None:
        kwargs["max_xc"] = args.max_xc
    if args.halogen_max_atoms is not None:
        kwargs["halogen_max_atoms"] = args.halogen_max_atoms
    if args.halogen_exhaustive is not None:
        kwargs["halogen_exhaustive"] = args.halogen_exhaustive
    if args.halogen_max_combinations is not None:
        kwargs["halogen_max_combinations"] = args.halogen_max_combinations
    if args.denoise_source is not None:
        kwargs["denoise_source"] = args.denoise_source
    if args.denoise_derivatives is not None:
        kwargs["denoise_derivatives"] = args.denoise_derivatives
    if args.element_ranges:
        try:
            kwargs["brutto_dict"] = _parse_element_ranges(args.element_ranges)
        except ValueError as e:
            print(f"Ошибка: неверный --element-ranges: {e}", file=sys.stderr)
            return 1

    # ── 2. Запуск пайплайна (прогресс → stderr) ────────────────────────────────
    try:
        with redirect_stdout(sys.stderr):
            if args.segment_width is not None:
                # Сегментный режим: RAW/mzML усредняются внутри отрезков
                # самой функцией; CSV/XLSX/JSON считаются одним сегментом.
                from src.core import run_pipeline_segmented

                res = run_pipeline_segmented(
                    src_path=args.input,
                    dmet_path=args.dmet,
                    dacet_path=args.dacet,
                    segment_width=args.segment_width,
                    rt_min=args.rt_min,
                    rt_max=args.rt_max,
                    **kwargs,
                )
            else:
                from src.core import run_pipeline

                warning = _halogen_warning(kwargs)
                if warning:
                    print(warning)

                src_path = _resolve_input(args.input)
                dmet_path = _resolve_input(args.dmet) if args.dmet else None
                dacet_path = _resolve_input(args.dacet) if args.dacet else None
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

    # Пайплайн мог вернуть результат с ошибками этапов (например, отсутствующие
    # файлы) — для CLI это код возврата 1. Предупреждения (визуализация,
    # Van Krevelen) не влияют на код возврата.
    if not getattr(res, "ok", True):
        for msg in getattr(res, "messages", None) or []:
            print(msg, file=sys.stderr)
        return 1

    # Предупреждения не делают результат недостоверным, но должны быть видны.
    for msg in getattr(res, "messages", None) or []:
        print(msg, file=sys.stderr)

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
