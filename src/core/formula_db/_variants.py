"""Варианты сжатой базы формул: что ставится всегда, а что — по выбору.

Правило инсталлера (решение заказчика):

* **CHNOSP** (36.2 МБ) ставится **всегда** и не выключается: выигрыш кратный,
  а объём мал — предлагать пользователю «скачать или не скачать» смысла нет;
* **отказ от базы** в инсталлер не выносится вовсе (остаётся внутренним
  резервом: если файлов нет, программа корректно переходит на перебор);
* **CHNOSPHal** предлагается как переключатель «или одно, или другое» ТОЛЬКО
  если его объём станет сопоставим с CHNOSP. Пока он примерно в 15 раз больше,
  выбора нет: ставится CHNOSP, а CHNOSPHal можно положить вручную (программа
  подхватит его автоматически как более быстрый).

Замеры — по ВСЕМУ пайплайну (set_01, загрузка → шумоподавление → назначение →
поиск серий → таблица), `tools/diagnostics/measure_db_variants.py`:

================  ==========  =================  ==============
вариант           объём       весь пайплайн      ускорение
================  ==========  =================  ==============
без базы          0           649 с              ×1
CHNOSP            36.2 МБ      18.4 с             ×18.8
CHNOSPHal         538 МБ       14.6 с             ×23.8
================  ==========  =================  ==============

Сравнивать по полному пайплайну важно: стадии загрузки, шумоподавления, поиска
серий и экспорта от базы не зависят. Замеры 16.10.2026 на свободной машине
(set_01, 316 пиков, чтение v3 уже реализовано): перебор 347.0 с (×1),
CHNOSP 18.42 с (×18.8), CHNOSPHal 14.59 с (×23.8). Отдельно на этапе
назначения: v2+слой 88 мс/пик против v3 28 мс/пик (×3.16).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

#: Переменная окружения для принудительного выбора варианта
#: (``chnosp`` | ``chorsphal`` | ``none``).
ENV_CHOICE = "NOM_FORMULA_DB"

#: Во сколько раз CHNOSPHal может быть больше CHNOSP, чтобы вообще имело смысл
#: предлагать переключатель в инсталлере.
SIZE_COMPARABLE_FACTOR = 3.0


@dataclass(frozen=True)
class FormulaDbVariant:
    """Описание варианта базы формул."""

    id: str
    title: str
    manifest: str
    formulas: int
    size_mb: float
    speedup: str
    description: str
    #: Больше — предпочтительнее при автоматическом выборе.
    priority: int
    #: Ставится всегда и не выключается пользователем (база по умолчанию).
    mandatory: bool = False
    #: Имя файла с данными (выводится из манифеста, если пусто).
    fdb: str = ""
    download_url: str | None = None


DB_VARIANTS: tuple[FormulaDbVariant, ...] = (
    FormulaDbVariant(
        id="chorsphal",
        title="CHNOSPHal — с галогенами (полная)",
        manifest="chorsphal_1000_v3.manifest.json",
        # Измерено сборкой 15–16.10.2026 (см. docs/formula_db_v3_report.md):
        # 7 860 непустых бинов, 2 376 074 334 формулы, 1.81 бит/формула,
        # .fdb 538.0 МБ + индекс 0.19 МБ.
        formulas=2_376_074_334,
        size_mb=538.2,
        speedup="×23.8",
        description=(
            "Материализованные галогенные варианты (F, Cl, Br, I до 5 атомов). "
            "Самый быстрый поиск: не нужно строить подстановки на лету. "
            "Самый большой объём."
        ),
        priority=20,
        download_url=None,  # появится вместе с релизом
    ),
    FormulaDbVariant(
        id="chnosp",
        title="CHNOSP — базовый (без галогенов)",
        manifest="chposp_1000_zstd9_v2.manifest.json",
        formulas=79_576_593,
        size_mb=36.2,
        speedup="×18.8",
        description=(
            "Базовые элементы C, H, N, O, S, P (79.6 млн формул). Галогены "
            "добавляются слоем подстановок на лету (×1.5–2 к времени поиска). "
            "36 МБ дают ускорение всего пайплайна примерно в 19 раз — "
            "рекомендуемый вариант по умолчанию."
        ),
        priority=10,
        download_url=None,
        mandatory=True,  # CHNOSP ставится всегда, выключать незачем
    ),
)


def search_dirs() -> list[Path]:
    """Каталоги поиска баз: проект, PyInstaller-бандл и user data."""
    import sys

    out: list[Path] = [Path(__file__).resolve().parents[3] / "data" / "formula_db"]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        out.append(Path(meipass) / "data" / "formula_db")
    try:
        from platformdirs import user_data_dir

        out.append(Path(user_data_dir("NOM-HRMS-FGA")))
    except Exception:
        pass
    return out


def _candidate_dirs(dirs: list[Path] | None = None) -> list[Path]:
    return list(dirs) if dirs is not None else search_dirs()


def find_variant_path(
    variant: FormulaDbVariant, dirs: list[Path] | None = None
) -> Path | None:
    """Путь к манифесту варианта, если он установлен."""
    if not variant.manifest:
        return None
    for d in _candidate_dirs(dirs):
        p = d / variant.manifest
        if not p.is_file():
            continue
        # Манифест без .fdb — недокачанная/битая установка.
        stem = variant.manifest[: -len(".manifest.json")]
        if (d / f"{stem}.fdb").is_file():
            return p
    return None


def mandatory_variants() -> list[FormulaDbVariant]:
    """Варианты, которые инсталлер ставит всегда (без вопроса)."""
    return [v for v in DB_VARIANTS if v.mandatory]


def installer_options() -> list[FormulaDbVariant]:
    """Что инсталлер предлагает на выбор.

    Пусто, пока объёмы несопоставимы: база по умолчанию ставится молча.
    Если появится вариант сопоставимого объёма (например, CHNOSPHal удастся
    ужать), вернётся список для переключателя «или одно, или другое».
    """
    base = [v for v in mandatory_variants()]
    if not base:
        return []
    base_size = max(v.size_mb for v in base) or 1.0
    options = []
    for v in DB_VARIANTS:
        if v.mandatory or v.size_mb <= 0:
            continue
        if v.size_mb <= base_size * SIZE_COMPARABLE_FACTOR:
            options.append(v)
    return options


def installer_plan() -> dict:
    """Что делать инсталлеру: что поставить молча и нужен ли переключатель."""
    mandatory = mandatory_variants()
    options = installer_options()
    return {
        "always": [v.id for v in mandatory],
        "choice": [v.id for v in options],
        "needs_choice": bool(options),
        "summary": (
            "выбор не нужен: база ставится по умолчанию"
            if not options
            else "предложить переключатель: " + ", ".join(v.title for v in options)
        ),
    }


def installed_variants(dirs: list[Path] | None = None) -> list[FormulaDbVariant]:
    """Установленные варианты (в порядке приоритета)."""
    found = [v for v in DB_VARIANTS if find_variant_path(v, dirs)]
    return sorted(found, key=lambda v: -v.priority)


def active_variant(
    dirs: list[Path] | None = None, choice: str | None = None
) -> FormulaDbVariant | None:
    """Какой вариант будет использован.

    Приоритет: явный выбор (аргумент или переменная окружения ``NOM_FORMULA_DB``)
    → самый приоритетный из установленных → ``None`` (перебор).
    """
    choice = (choice or os.environ.get(ENV_CHOICE) or "").strip().lower()
    if choice in ("none", "off", "0"):
        return None
    if choice:
        for v in DB_VARIANTS:
            if v.id == choice and find_variant_path(v, dirs):
                return v
        return None
    installed = installed_variants(dirs)
    return installed[0] if installed else None


def variants_report(dirs: list[Path] | None = None) -> list[dict]:
    """Данные для диалога/CLI: варианты, объём, ускорение, установлен ли."""
    rows = []
    for v in sorted(DB_VARIANTS, key=lambda x: -x.priority):
        path = find_variant_path(v, dirs)
        rows.append(
            {
                "id": v.id,
                "title": v.title,
                "size_mb": v.size_mb,
                "formulas": v.formulas,
                "speedup": v.speedup,
                "installed": bool(path),
                "path": str(path) if path else "",
                "description": v.description,
                "download_url": v.download_url,
            }
        )
    return rows


def describe_choice(dirs: list[Path] | None = None) -> str:
    """Короткая строка: какой вариант активен."""
    v = active_variant(dirs)
    if v is None:
        return "база не используется (перебор формул)"
    return f"{v.title} ({v.size_mb:.0f} МБ, ускорение {v.speedup})"
