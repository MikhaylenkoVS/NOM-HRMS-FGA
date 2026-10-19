"""Сплошная инвентаризация кода конкурентов: файлы, символы, операции.

Задача заказчика: собрать информацию обо ВСЕХ операциях, без «избранного»,
в первозданном виде. Поэтому скрипт не выбирает «важное», а:

  1. обходит все исходные файлы проекта (по расширениям языков);
  2. считает строки (физические/непустые/байты) по каждому файлу;
  3. строит индекс символов (классы/функции/методы) по языкам;
  4. для каждого набора ключевых слов операции находит все вхождения
     (файл:строка + текст строки), считает их число;
  5. сохраняет результат в JSON (по проекту и сводный).

Запуск (из корня проекта):
  python tools/diagnostics/audit_competitors.py --root D:/Temp/User/competitors \
      --out docs/competitors/raw --hit-cap 5000
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

# ── Языки и расширения ─────────────────────────────────────────────────────
LANG_BY_EXT = {
    ".py": "python",
    ".r": "r",
    ".R": "r",
    ".java": "java",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".c": "c",
    ".m": "matlab",
    ".cpp.in": "cpp",
}
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
    "target",
    "bin",
    "obj",
    "packages",
    ".venv",
    "venv",
    "docs",
    "test",
    "tests",
    "testdata",
    "TestData",
    "examples",
    "data",
}

# ── Операции: ключевые слова для поиска ────────────────────────────────────
OPERATIONS: dict[str, list[str]] = {
    "raw_vendor_io": [
        r"\bthermo\b",
        r"\.raw\b",
        r"bruker",
        r"waters",
        r"mzml",
        r"mzxml",
        r"netcdf",
        r"imzml",
        r"rawfile",
        r"xcalibur",
        r"compass",
    ],
    "transient_ft": [
        r"transient",
        r"apodiz",
        r"zero[-_ ]?fill",
        r"\bfft\b",
        r"fourier",
        r"magnitude",
        r"frequency[_ ]domain",
        r"phase\b",
    ],
    "profile_preprocessing": [
        r"baseline",
        r"smooth",
        r"denois",
        r"noise[_ ]reduc",
        r"background[_ ]subtract",
        r"co[-_ ]?add",
        r"averag",
    ],
    "peak_picking_centroiding": [
        r"peak[_ ]?picking",
        r"centroid",
        r"local[_ ]max",
        r"apex",
        r"\bfwhm\b",
        r"resolving[_ ]power",
        r"valley",
        r"peak[_ ]height",
        r"peak[_ ]area",
    ],
    "noise_estimation": [
        r"noise[_ ]?threshold",
        r"noise[_ ]?level",
        r"sn[_ ]?cut",
        r"signal[_ ]to[_ ]noise",
        r"\bs/n\b",
        r"quantile",
        r"kendrick.*noise",
        r"histnoise",
        r"bayes",
    ],
    "mass_calibration": [
        r"calibrat",
        r"lock[_ ]?mass",
        r"recalib",
        r"reference[_ ]mass",
        r"mass[_ ]error",
        r"robust[_ ]?(fit|calib)",
        r"polynomial",
        r"ledford",
    ],
    "rt_alignment": [
        r"retention[_ ]time|rt[_ ]?align|alignment|\bwarp\b|loess|obiwarp",
    ],
    "chromatographic_features": [
        r"chromatogram",
        r"\bxic\b",
        r"\beic\b",
        r"feature",
        r"deconvolut",
        r"peak[_ ]?shape",
        r"elution",
    ],
    "gap_filling": [r"gap[_ ]?fill", r"fillpeaks", r"missing[_ ]value", r"imput"],
    "isotope_detection": [
        r"isotop",
        r"\b13c\b|maxo|c13",
        r"\b34s\b|s34",
        r"\bm\+1\b",
        r"m\+2",
        r"fine[_ ]isotop",
        r"isotopologue",
        r"monoisotopic",
    ],
    "adduct_ion_identity": [
        r"adduct",
        r"ion[_ ]identity",
        r"protonat",
        r"deprotonat",
        r"sodiat",
        r"\bnh4\b|ammonium",
        r"dimer",
        r"in[-_ ]?source",
        r"ion[_ ]?mode",
        r"\bm\+h\b|\bm-h\b",
    ],
    "charge_state": [
        r"charge[_ ]?state",
        r"\bcharge\b",
        r"\bz\s*=\s*\d",
        r"zmax|charge_max",
    ],
    "formula_assignment": [
        r"formula[_ ]?(assign|search|generat|find)",
        r"molecular[_ ]?formula",
        r"brutto",
        r"mass[_ ]?decomposit",
        r"composition",
        r"candidate",
        r"assign_formulas",
    ],
    "formula_scoring": [
        r"\bscore\b|scoring",
        r"\bppm\b",
        r"mass[_ ]?accuracy",
        r"confidence",
        r"\brank\b|ranking",
        r"priorit",
    ],
    "ambiguity_handling": [
        r"ambigu",
        r"unambiguous",
        r"unassigned",
        r"multiple[_ ]candidates",
        r"candidate[_ ]list",
        r"tie[-_ ]?break",
    ],
    "chemical_rules": [
        r"valence",
        r"\bdbe\b|rdbe|ihd",
        r"nitrogen[_ ]rule",
        r"senior",
        r"element[_ ]?(range|limit|filter)",
        r"plausib",
        r"chemical[_ ]rule",
    ],
    "halogen_support": [
        # Однобуквенные шаблоны («I», «F», «Cl») давали ложные срабатывания
        # на переменных, поэтому ищем только содержательные формы.
        r"halogen",
        r"heteroatom",
        r"chlor|cloro|cl_?count|n_?cl",
        r"brom|br_?count|n_?br",
        r"iod|iodo|n_?i\b",
        r"fluor|n_?f\b",
        r"\bxf\b|\bxs\b|\bxcount\b|halogen_?count",
        # Символы элементов — только в «строковом» виде, иначе одиночные буквы
        # F/Cl/Br/I совпадают с чем угодно (проверено: давало сотни тысяч ложных).
        r'["\']Cl["\']|["\']Br["\']|["\']F["\']|["\']I["\']',
        r"\bCl_?count\b|\bBr_?count\b|\bF_?count\b|\bI_?count\b",
    ],
    "internal_recalibration_series": [
        r"homologous",
        r"recalibrant",
        r"internal[_ ]?(series|calibrat)",
        r"series.*(cd3|cd3co)",
    ],
    "kendrick": [r"kendrick", r"\bkmd\b", r"mass[_ ]defect"],
    "descriptors": [
        r"van[_ ]?krevelen",
        r"aromatic",
        r"\bai\b|\bcai\b|nosc",
        r"h/c|o/c",
        r"molecular[_ ]?(class|metric|descriptor)",
        r"dbe[_ ]?vs",
    ],
    "similarity": [r"similar|cosine|jaccard|distance[_ ]?matrix|correlat"],
    "statistics": [
        r"\bpca\b|principal[_ ]component",
        r"\bpls\b|partial[_ ]least",
        r"cluster",
        r"dbscan",
        r"\bt[-_ ]?test\b|anova|volcano",
        r"hierarch",
    ],
    "visualization": [
        r"\bplot\b|figure|chart",
        r"heatmap",
        r"scatter",
        r"histogram",
        r"network[_ ]?graph|graphml|cytoscape",
    ],
    "msms": [
        r"ms/?ms|ms2|tandem",
        r"fragment",
        r"neutral[_ ]loss",
        r"spectral[_ ]librar",
        r"product[_ ]ion|precursor",
    ],
    "ion_mobility_ccs": [
        r"ion[_ ]?mobility|\bims\b|\btims\b|drift",
        r"\bccs\b|collision[_ ]cross",
    ],
    "molecular_networking": [r"molecular[_ ]network", r"network[_ ]?analysis"],
    "qc_metrics": [
        r"\bqc\b|quality[_ ]control",
        r"blank",
        r"carryover",
        r"\bcv\b|coefficient[_ ]of[_ ]variation",
        r"mzqc|qcml",
        r"drift",
    ],
    "provenance_workflow": [
        r"workflow",
        r"pipeline",
        r"provenance",
        r"\brecipe\b",
        r"\bbatch\b",
        r"metadata",
        r"parameter[_ ]?(export|file|schema)",
        r"hdf5|\.h5\b",
        r"random[_ ]seed",
    ],
    "io_export": [
        r"\bcsv\b",
        r"\bxlsx\b|\bexcel\b",
        r"\bjson\b",
        r"\bhdf5\b",
        r"to_csv|to_excel|write_csv|write\.table",
    ],
}

# ── Регулярные выражения символов ──────────────────────────────────────────
SYMBOL_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "python": [
        ("class", r"^(?P<ind>\s*)class\s+(?P<name>\w+)"),
        ("def", r"^(?P<ind>\s*)(?:async\s+)?def\s+(?P<name>\w+)"),
    ],
    "r": [
        # В R функции часто объявлены с отступом и через <<- или обычное =
        (
            "function",
            r"^\s*(?P<name>[A-Za-z_.][\w.]*)\s*(?:<<-|<-|=)\s*function\s*\(",
        ),
        ("s4_method", r"^\s*setMethod\s*\(\s*[\"'](?P<name>[\w.]+)"),
        ("s4_generic", r"^\s*setGeneric\s*\(\s*[\"'](?P<name>[\w.]+)"),
    ],
    "java": [
        (
            "type",
            r"^\s*(?:public|private|protected|static|final|abstract|\s)*\b(?:class|interface|enum|record)\s+(?P<name>\w+)",
        ),
        (
            "method",
            r"^\s{2,}(?:public|private|protected|static|final|synchronized|abstract|native|default|\s)+[\w<>\[\],.?\s]+?\s+(?P<name>\w+)\s*\(",
        ),
    ],
    "csharp": [
        (
            "type",
            r"^\s*(?:public|private|protected|internal|static|sealed|abstract|partial|\s)*\b(?:class|interface|enum|record|struct)\s+(?P<name>\w+)",
        ),
        (
            "method",
            r"^\s{2,}(?:public|private|protected|internal|static|virtual|override|async|\s)+[\w<>\[\],.?]+\s+(?P<name>\w+)\s*\(",
        ),
    ],
    "cpp": [
        ("type", r"^\s*(?:class|struct|union)\s+(?P<name>\w+)"),
        ("function", r"^[A-Za-z_][\w:<>~*&,\s]*\s+(?P<name>[A-Za-z_]\w*)\s*\("),
    ],
}
SYMBOL_PATTERNS["c"] = [
    ("function", r"^[A-Za-z_][\w:*\s]*\s+(?P<name>[A-Za-z_]\w*)\s*\(")
]


def git_info(path: Path) -> dict:
    out: dict = {}
    for key, args in (
        ("commit", ["rev-parse", "HEAD"]),
        ("commit_date", ["log", "-1", "--format=%cI"]),
        ("remote", ["config", "--get", "remote.origin.url"]),
    ):
        try:
            out[key] = subprocess.run(
                ["git", "-C", str(path), *args],
                capture_output=True,
                text=True,
                timeout=30,
            ).stdout.strip()
        except Exception:
            out[key] = ""
    return out


def read_license(path: Path) -> dict:
    candidates: list[Path] = []
    for name in (
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "COPYING",
        "COPYING.txt",
        "LICENSE-MIT",
        "license",
        "THIRD-PARTY-LICENSE-README.md",
    ):
        f = path / name
        if f.is_file():
            candidates.append(f)
    # Иногда файл лицензии лежит не в корне или назван иначе (например, у MS-DIAL
    # в корне только THIRD-PARTY-LICENSE-README.md). Ищем любые *licen*/*copying*
    # на глубине до двух уровней и фиксируем все найденные.
    extra: list[str] = []
    for pattern in ("*licen*", "*copying*", "*LICENSE*", "*COPYING*"):
        for f in list(path.glob(pattern))[:5] + list(path.glob(f"*/{pattern}"))[:5]:
            if f.is_file() and f not in candidates:
                extra.append(str(f.relative_to(path)).replace("\\", "/"))

    found: list[str] = [str(c.relative_to(path)).replace("\\", "/") for c in candidates]
    for name in extra:
        if name not in found:
            found.append(name)

    for f in candidates:
        if True:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            low = text.lower()
            # Лицензию определяем по НАЧАЛУ файла: полные тексты GPL/AGPL/LGPL
            # упоминают друг друга в разделе «How to Apply», из-за чего наивный
            # поиск по всему файлу ошибается (GPL-3 -> AGPL, GPL-2 -> LGPL).
            # Поэтому для GNU-семейства смотрим ЗАГОЛОВОК: «GNU [AFFERO|LESSER]
            # GENERAL PUBLIC LICENSE» — вариант стоит между GNU и GENERAL.
            head = low[:2000]
            spdx = "unknown"
            m_title = re.search(
                r"gnu\s+(affero\s+|lesser\s+|library\s+)?general public license", head
            )
            if m_title:
                variant = (m_title.group(1) or "").strip()
                spdx = {"affero": "AGPL", "lesser": "LGPL", "library": "LGPL"}.get(
                    variant, "GPL"
                )
            if spdx == "unknown":
                for key, val in (
                    # BSD-2/BSD-3 не содержат слова «BSD» — ловим по формуле
                    ("redistribution and use in source and binary forms", "BSD"),
                    ("bsd", "BSD"),
                    ("permission is hereby granted, free of charge", "MIT"),
                    ("mit license", "MIT"),
                    ("apache license", "Apache"),
                    ("mozilla public license", "MPL"),
                    ("gnu affero", "AGPL"),
                    ("lesser general public", "LGPL"),
                    ("gnu general public license", "GPL"),
                    ("general public license", "GPL"),
                ):
                    if key in head:
                        spdx = val
                        break
            if spdx == "unknown":
                for key, val in (
                    ("gnu affero", "AGPL"),
                    ("lesser general public", "LGPL"),
                    ("general public license", "GPL"),
                    ("bsd", "BSD"),
                    ("mit", "MIT"),
                    ("apache", "Apache"),
                    ("mozilla public", "MPL"),
                ):
                    if key in low:
                        spdx = val
                        break
            ver = ""
            m = re.search(r"version\s+(\d+(?:\.\d+)?)", low)
            if m:
                ver = m.group(1)
            return {
                "file": str(f.relative_to(path)).replace("\\", "/"),
                "spdx_guess": f"{spdx}-{ver}" if ver else spdx,
                "head": " ".join(text[:300].split()),
                "license_files_found": found,
            }
    return {
        "file": None,
        "spdx_guess": "NO_LICENSE_FILE",
        "head": "",
        "license_files_found": found,
        "note": "файл лицензии проекта не найден"
        + (f"; найдены только: {', '.join(found)}" if found else ""),
    }


def iter_source_files(root: Path, langs: set[str] | None = None):
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        ext = p.suffix if p.suffix != ".R" else ".R"
        lang = LANG_BY_EXT.get(ext) or LANG_BY_EXT.get(ext.lower())
        if not lang:
            continue
        if langs and lang not in langs:
            continue
        yield p, lang


def scan_project(pid: str, root: Path, hit_cap: int) -> tuple[dict, dict, dict]:
    """Возвращает (index, operations, summary)."""
    info = git_info(root)
    lic = read_license(root)
    files: list[dict] = []
    symbols: list[dict] = []
    op_hits: dict[str, list[dict]] = {op: [] for op in OPERATIONS}
    op_totals: dict[str, int] = {op: 0 for op in OPERATIONS}
    op_files: dict[str, set[str]] = {op: set() for op in OPERATIONS}
    total_bytes = 0
    total_lines = 0

    compiled = {
        op: [re.compile(rx, re.I) for rx in rxs] for op, rxs in OPERATIONS.items()
    }

    for p, lang in iter_source_files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = p.relative_to(root).as_posix()
        lines = text.splitlines()
        n_lines = len(lines)
        n_nonempty = sum(1 for ln in lines if ln.strip())
        n_bytes = len(text.encode("utf-8", errors="replace"))
        files.append(
            {
                "file": rel,
                "lang": lang,
                "lines": n_lines,
                "nonempty": n_nonempty,
                "bytes": n_bytes,
            }
        )
        total_bytes += n_bytes
        total_lines += n_lines

        # символы
        patterns = SYMBOL_PATTERNS.get(lang, [])
        if patterns:
            for i, line in enumerate(lines, 1):
                if not line.strip() or len(line) > 400:
                    continue
                for kind, rx in patterns:
                    m = re.match(rx, line)
                    if m:
                        symbols.append(
                            {
                                "file": rel,
                                "line": i,
                                "kind": kind,
                                "name": m.group("name"),
                                "text": line.strip()[:200],
                            }
                        )
                        break

        # операции
        for op, rxs in compiled.items():
            for i, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                if any(rx.search(line) for rx in rxs):
                    op_totals[op] += 1
                    op_files[op].add(rel)
                    if len(op_hits[op]) < hit_cap:
                        op_hits[op].append(
                            {
                                "file": rel,
                                "line": i,
                                "text": line.strip()[:220],
                            }
                        )

    langs_count: dict[str, int] = {}
    for f in files:
        langs_count[f["lang"]] = langs_count.get(f["lang"], 0) + 1

    # Честно фиксируем, что осталось за рамками сканирования (тесты, данные,
    # примеры, сборка): считаем исходные файлы в пропущенных каталогах.
    skipped: dict[str, int] = {}
    for p in root.rglob("*"):
        if p.is_dir() or not p.suffix:
            continue
        lang = LANG_BY_EXT.get(p.suffix) or LANG_BY_EXT.get(p.suffix.lower())
        if not lang:
            continue
        for part in p.parts:
            if part in SKIP_DIRS:
                skipped[part] = skipped.get(part, 0) + 1
                break

    index = {
        "project": pid,
        "path": str(root),
        "git": info,
        "license": lic,
        "inventory": {
            "files": len(files),
            "by_language": langs_count,
            "total_lines": total_lines,
            "total_bytes": total_bytes,
            "per_file": sorted(files, key=lambda f: -f["lines"]),
        },
        "symbols_count": len(symbols),
        "symbols": symbols,
        "skipped_source_files_by_dir": skipped,
    }
    operations = {
        "project": pid,
        "note": "Сырые вхождения ключевых слов по операциям. Ограничение на длину "
        "списка на операцию задано --hit-cap; общее число вхождений точное.",
        "operations": {
            op: {
                "total_hits": op_totals[op],
                "files": sorted(op_files[op]),
                "hits": op_hits[op],
                "truncated": op_totals[op] > len(op_hits[op]),
            }
            for op in OPERATIONS
        },
    }
    summary = {
        "project": pid,
        "git_commit": info.get("commit", ""),
        "license": lic.get("spdx_guess"),
        "files": len(files),
        "lines": total_lines,
        "by_language": langs_count,
        "operations": {
            op: {"hits": op_totals[op], "files": len(op_files[op])} for op in OPERATIONS
        },
    }
    return index, operations, summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="D:/Temp/User/competitors")
    ap.add_argument("--out", default="docs/competitors/raw")
    ap.add_argument("--hit-cap", type=int, default=5000)
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()

    root = Path(a.root)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    projects = sorted(
        p for p in root.iterdir() if p.is_dir() and p.name != "__pycache__"
    )
    if a.only:
        projects = [p for p in projects if p.name in a.only]

    combined = []
    for proj in projects:
        print(f"сканирую {proj.name} ...", flush=True)
        index, operations, summary = scan_project(proj.name, proj, a.hit_cap)
        (out / f"{proj.name}_index.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        (out / f"{proj.name}_operations.json").write_text(
            json.dumps(operations, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        combined.append(summary)
        print(
            f"  файлов {summary['files']}, строк {summary['lines']}, "
            f"символов {index['symbols_count']}, лицензия {summary['license']}",
            flush=True,
        )

    (out / "_combined_summary.json").write_text(
        json.dumps({"projects": combined}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\nсводка: {out / '_combined_summary.json'}")


if __name__ == "__main__":
    main()
