"""Читатель сжатой базы формул формата v3 (CHNOSPHal — с галогенами).

Формат v3 (сборщик — ``tools/diagnostics/build_halogen_db.py``, отчёт —
``docs/formula_db_v3_report.md``):

* запись — 6 байт: код ``C(8) | N(7) | O(7) | S(6) | P(7) | X(7)``;
* ``X`` — код мультимножества галогенов: 0 = без галогенов, 1..N — комбинации
  до ``halogen_cap`` атомов (F, Cl, Br, I); порядок кодов задаётся таблицей
  :func:`_multiset_table` и полностью воспроизводим;
* **водород в записи не хранится**: он однозначно восстанавливается по границам
  бина (0.1 Да) и условиям модели — ``h ≡ N+P (mod 2)`` (целое DBE),
  ``h ≤ min(255, 2C+2+N+P)`` (DBE ≥ 0), ``h ≥ x`` (водород каркаса не меньше
  числа заместителей). Так как шаг по H ≈ 1.0078 Да больше ширины бина, в бине
  на один код приходится не более одного h;
* **семантика водорода**: восстановленный ``h`` — это водород КАРКАСА (до
  замещения). Фактическое число атомов водорода в формуле — ``H = h − x``, где
  ``x`` — суммарное число атомов галогенов (каждый заместил один водород).
  Читатель возвращает именно фактическое ``H``, а ``exact_mass`` уже учитывает
  замещение (в Δ входит ``−x·m(H)``). Ранее читатель возвращал каркасный ``h`` —
  это давало расхождение со слоем подстановок базы v2 при совпадающих массах;
* блок = дельта-кодирование по возрастанию кода, byte-shuffle по столбцам,
  кадр zstd;
* индекс — 24 байта на бин (``<IQIII>``: бин, смещение, сжатый размер,
  распакованный размер, число записей), отсортирован по бину; бинов, в которых
  нет ни одной формулы, в индексе нет (это нормально — см.
  ``tools/diagnostics/empty_bins_report.py``).

Публичный API совпадает с форматом v2 (``_reader.FormulaDatabaseReader``):
``search(mass, ppm=..., element_filter=..., max_results=...)`` возвращает
объекты с полями ``counts`` и ``exact_mass``, поэтому пайплайн работает без
изменений.
"""

from __future__ import annotations

import itertools
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import zstandard as zstd

logger = logging.getLogger(__name__)

#: Совпадает с форматом сборщика: 1e-11 Да на единицу, бин 0.1 Да.
MASS_SCALE = 100_000_000_000
BIN_WIDTH_U = 10_000_000_000

MASS_U = {
    "C": 1_200_000_000_000,
    "H": 100_782_503_223,
    "N": 1_400_307_400_443,
    "O": 1_599_491_461_957,
    "S": 3_197_207_117_440,
    "P": 3_097_376_199_842,
    "F": 1_899_840_316_273,
    "Cl": 3_496_885_268_200,
    "Br": 7_891_833_760_000,
    "I": 12_690_447_190_000,
}
H_U = MASS_U["H"]
HALO = ("F", "Cl", "Br", "I")

#: Порядок элементов в строке формулы — как в остальном приложении.
FORMULA_ELEMENT_ORDER = ("C", "H", "O", "N", "S", "P", "F", "Cl", "Br", "I")

RECORD_BYTES = 6
INDEX_RECORD = 24


@dataclass(slots=True)
class SearchResult:
    """Одна найденная формула: количества атомов и точная масса (в Да)."""

    counts: dict[str, int]
    exact_mass: float
    formula: str = ""


@dataclass(slots=True)
class _BinData:
    """Распакованный бин: параллельные массивы по записям."""

    mass_u: np.ndarray  # int64, единицы 1e-11 Да
    counts: np.ndarray  # int32, столбцы в FORMULA_ELEMENT_ORDER (10)


def _multiset_table(cap: int) -> tuple[np.ndarray, np.ndarray]:
    """Таблица кодов галогенов: (Δ по коду, количества атомов по коду).

    Возвращает
    ----------
    deltas : np.ndarray, shape (n_codes,)
        Δ = Σ n_x (m_X − m_H) в единицах 1e-11 Да.
    halo_counts : np.ndarray, shape (n_codes, 4)
        Количества F, Cl, Br, I для каждого кода (порядок — :data:`HALO`).
    """
    deltas: list[int] = [0]
    halo: list[list[int]] = [[0, 0, 0, 0]]
    seen: list[tuple[tuple[str, int], ...]] = [()]
    for size in range(1, max(0, cap) + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            if collapsed in seen:
                continue
            seen.append(collapsed)
            delta = sum(n * (MASS_U[el] - H_U) for el, n in collapsed)
            deltas.append(delta)
            row = [0, 0, 0, 0]
            for el, n in collapsed:
                row[HALO.index(el)] = n
            halo.append(row)
    return np.asarray(deltas, dtype=np.int64), np.asarray(halo, dtype=np.int64)


class FormulaDatabaseReaderV3:
    """Чтение базы формата v3 (CHNOSPHal) с кэшем распакованных бинов."""

    format_version = 3
    #: В этой базе галогены уже «запечены» — слой подстановок не нужен.
    has_halogens = True

    def __init__(
        self,
        manifest_path: str | Path,
        cache_size: int = 64,
        verify: bool = False,
    ) -> None:
        self._manifest_path = Path(manifest_path)
        self._manifest = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        version = int(self._manifest.get("format_version", 0) or 0)
        if version != 3:
            raise ValueError(
                f"Манифест {self._manifest_path.name}: формат {version}, нужен v3"
            )
        self._cap = int(self._manifest.get("halogen_cap", 5))
        self._verify = verify
        self._deltas, self._halo = _multiset_table(self._cap)
        self._x_total = self._halo.sum(axis=1).astype(np.int64)

        self._fdb = self._resolve_sibling(".fdb")
        self._idx = self._resolve_sibling(".idx")
        self._file = None
        self._cache: dict[int, _BinData] = {}
        self._cache_order: list[int] = []
        self._cache_size = max(1, int(cache_size))
        self._load_index()

    # ── открытие/служебное ────────────────────────────────────────────────
    def _resolve_sibling(self, suffix: str) -> Path:
        """Файл данных ищем рядом с манифестом (пути в манифесте — машинные)."""
        name = self._manifest_path.name
        stem = (
            name[: -len(".manifest.json")] if name.endswith(".manifest.json") else name
        )
        sibling = self._manifest_path.parent / f"{stem}{suffix}"
        if sibling.is_file():
            return sibling
        fallback = self._manifest.get(suffix.lstrip("."))
        return Path(fallback) if fallback else sibling

    def _load_index(self) -> None:
        raw = self._idx.read_bytes()
        if len(raw) % INDEX_RECORD:
            raise ValueError(f"Индекс {self._idx.name}: размер не кратен записи")
        n = len(raw) // INDEX_RECORD
        arr = np.frombuffer(
            raw,
            dtype=np.dtype(
                [
                    ("bin", "<u4"),
                    ("off", "<u8"),
                    ("comp", "<u4"),
                    ("raw", "<u4"),
                    ("count", "<u4"),
                ]
            ),
        )
        if len(arr) != n:  # pragma: no cover - защита от несовпадения разметки
            raise ValueError("Индекс: не удалось разобрать записи")
        self._bins = np.ascontiguousarray(arr["bin"], dtype=np.int64)
        self._offsets = np.ascontiguousarray(arr["off"], dtype=np.int64)
        self._comps = np.ascontiguousarray(arr["comp"], dtype=np.int64)
        self._raws = np.ascontiguousarray(arr["raw"], dtype=np.int64)
        self._counts = np.ascontiguousarray(arr["count"], dtype=np.int64)
        if len(self._bins) and not np.all(np.diff(self._bins) > 0):
            raise ValueError("Индекс должен быть отсортирован по бину")

    @property
    def manifest(self) -> dict:
        return self._manifest

    @property
    def total_formulas(self) -> int:
        records = self._manifest.get("records")
        if records:
            return int(records)
        return int(self._counts.sum())

    @property
    def max_mass(self) -> float:
        rng = self._manifest.get("range_da") or [0.0, 0.0]
        return float(rng[1])

    @property
    def halogen_cap(self) -> int:
        return self._cap

    def bin_ids(self, mass_lo: float, mass_hi: float) -> np.ndarray:
        """Бины базы, попадающие в окно масс [масса_lo, масса_hi] (в Да)."""
        lo = max(0, int(mass_lo * MASS_SCALE)) // BIN_WIDTH_U
        hi = max(0, int(mass_hi * MASS_SCALE)) // BIN_WIDTH_U
        if hi < lo:
            return np.zeros(0, dtype=np.int64)
        left = np.searchsorted(self._bins, lo, side="left")
        right = np.searchsorted(self._bins, hi, side="right")
        return self._bins[left:right]

    def bin_data(self, bin_id: int) -> _BinData | None:
        """Распакованный бин целиком (низкоуровневый пакетный доступ).

        ``None``, если бина нет в базе (в нижней области масс это норма:
        см. ``tools/diagnostics/empty_bins_report.py``).
        """
        pos = self._position(bin_id)
        if pos < 0:
            return None
        return self._bin_data(pos)

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
        self._cache.clear()
        self._cache_order.clear()

    def __enter__(self) -> "FormulaDatabaseReaderV3":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ── распаковка ────────────────────────────────────────────────────────
    def _position(self, bin_id: int) -> int:
        pos = int(np.searchsorted(self._bins, bin_id, side="left"))
        if pos >= len(self._bins) or self._bins[pos] != bin_id:
            return -1
        return pos

    def _open(self) -> None:
        if self._file is None:
            self._file = open(self._fdb, "rb")

    def _decode_codes(self, raw: bytes, count: int) -> np.ndarray:
        """6 байт/запись, дельта по возрастанию → массив кодов."""
        if count == 0:
            return np.zeros(0, dtype=np.uint64)
        arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, count).T
        padded = np.zeros((count, 8), dtype=np.uint8)
        padded[:, :RECORD_BYTES] = arr
        deltas = padded.view(np.uint64).reshape(count)
        return np.cumsum(deltas)

    def _bin_data(self, pos: int) -> _BinData:
        cached = self._cache.get(pos)
        if cached is not None:
            return cached
        count = int(self._counts[pos])
        bin_id = int(self._bins[pos])
        self._open()
        self._file.seek(int(self._offsets[pos]))
        blob = self._file.read(int(self._comps[pos]))
        if len(blob) != int(self._comps[pos]):
            raise RuntimeError(
                f"Бин {bin_id}: прочитано {len(blob)} вместо {int(self._comps[pos])}"
            )
        raw = zstd.ZstdDecompressor().decompress(
            blob, max_output_size=int(self._raws[pos])
        )
        if len(raw) != int(self._raws[pos]):
            raise RuntimeError(
                f"Бин {bin_id}: распаковано {len(raw)} вместо {int(self._raws[pos])}"
            )
        codes = self._decode_codes(raw, count)

        c = (codes & 0xFF).astype(np.int64)
        nv = ((codes >> 8) & 0x7F).astype(np.int64)
        o = ((codes >> 15) & 0x7F).astype(np.int64)
        sv = ((codes >> 22) & 0x3F).astype(np.int64)
        pv = ((codes >> 28) & 0x7F).astype(np.int64)
        xcode = ((codes >> 35) & 0x7F).astype(np.int64)

        delta = self._deltas[xcode]
        x_atoms = self._x_total[xcode]
        halo = self._halo[xcode]

        fw = (
            c * MASS_U["C"]
            + nv * MASS_U["N"]
            + o * MASS_U["O"]
            + sv * MASS_U["S"]
            + pv * MASS_U["P"]
            + delta
        )
        lo_u = bin_id * BIN_WIDTH_U
        hi_u = lo_u + BIN_WIDTH_U
        parity = (nv + pv) & 1
        h_cap = np.minimum(255, 2 * c + nv + pv + 2)
        # ceil((lo - fw) / H_U) и приведение к нужной чётности
        h_lo = np.maximum.reduce([parity, x_atoms, -((-(lo_u - fw)) // H_U)])
        h_lo = h_lo + ((h_lo - parity) & 1)
        h_hi = np.minimum(h_cap, (hi_u - 1 - fw) // H_U)
        ok = h_lo <= h_hi
        if not np.all(ok):
            bad = int(ok.size - ok.sum())
            logger.warning(
                "Бин %d: %d записей не восстанавливаются по H (пропущены)", bin_id, bad
            )
        h = np.where(ok, h_lo, 0)

        counts = np.zeros((count, len(FORMULA_ELEMENT_ORDER)), dtype=np.int32)
        counts[:, 0] = c  # C
        # ВАЖНО: в базе хранится «каркасный» водород h (до замещения), поэтому
        # фактическое число атомов H в формуле = h - x (каждый галоген заместил
        # один водород). Масса при этом уже посчитана с учётом замещения (delta
        # содержит -x*m_H), поэтому менять mass_u не нужно.
        counts[:, 1] = np.maximum(h - x_atoms, 0)  # H
        counts[:, 2] = o  # O
        counts[:, 3] = nv  # N
        counts[:, 4] = sv  # S
        counts[:, 5] = pv  # P
        counts[:, 6:10] = halo.astype(np.int32)  # F, Cl, Br, I

        mass_u = fw + h * H_U
        data = _BinData(mass_u=mass_u[ok], counts=counts[ok])
        # кэш (простой LRU)
        self._cache[pos] = data
        self._cache_order.append(pos)
        while len(self._cache_order) > self._cache_size:
            old = self._cache_order.pop(0)
            self._cache.pop(old, None)
        return data

    # ── поиск ─────────────────────────────────────────────────────────────
    def search(
        self,
        mass: float,
        ppm: float = 5.0,
        element_filter: dict[str, tuple[int, int]] | None = None,
        max_results: int = 500,
    ) -> list[SearchResult]:
        """Формулы в окне ``mass ± ppm``.

        Parameters
        ----------
        mass : float
            Целевая масса (Да).
        ppm : float
            Полуширина окна в ppm.
        element_filter : dict or None
            Ограничения ``{элемент: (минимум, максимум)}``; элементы, которых нет
            в базе (например, из конфигурации), игнорируются.
        max_results : int
            Сколько лучших (по отклонению массы) результатов вернуть.
        """
        if mass <= 0 or ppm <= 0 or max_results <= 0:
            return []
        center_u = int(round(mass * MASS_SCALE))
        tol_u = int(abs(center_u) * ppm * 1e-6) + 1
        lo_u, hi_u = center_u - tol_u, center_u + tol_u
        if hi_u <= 0:
            return []

        pos_lo = int(np.searchsorted(self._bins, max(0, lo_u) // BIN_WIDTH_U, "left"))
        pos_hi = int(np.searchsorted(self._bins, hi_u // BIN_WIDTH_U, "right"))
        if pos_hi <= pos_lo:
            return []

        found: list[tuple[int, int, int]] = []  # (|Δ|, масса_u, позиция в собранном)
        collected: list[tuple[np.ndarray, np.ndarray]] = []
        for pos in range(pos_lo, pos_hi):
            data = self._bin_data(pos)
            if data.mass_u.size == 0:
                continue
            mask = (data.mass_u >= lo_u) & (data.mass_u <= hi_u)
            if element_filter:
                for el, (lo, hi) in element_filter.items():
                    if el not in FORMULA_ELEMENT_ORDER:
                        continue
                    col = data.counts[:, FORMULA_ELEMENT_ORDER.index(el)]
                    if lo > 0:
                        mask &= col >= int(lo)
                    if hi < 255:
                        mask &= col <= int(hi)
            if not mask.any():
                continue
            masses = data.mass_u[mask]
            counts = data.counts[mask]
            base = sum(c.size for c, _ in collected)
            collected.append((masses, counts))
            for i, m in enumerate(masses):
                found.append((abs(int(m) - center_u), int(m), base + i))

        if not found:
            return []
        found.sort(key=lambda t: t[0])
        found = found[:max_results]

        counts_all = (
            np.concatenate([c[1] for c in collected])
            if collected
            else np.zeros((0, len(FORMULA_ELEMENT_ORDER)), np.int32)
        )
        out: list[SearchResult] = []
        for _delta, mass_u, idx in found:
            row = counts_all[idx]
            # Возвращаем ВСЕ элементы (включая нулевые) — предсказуемый словарь
            # для вызывающего кода и тестов.
            counts = {el: int(row[j]) for j, el in enumerate(FORMULA_ELEMENT_ORDER)}
            out.append(
                SearchResult(
                    counts=counts,
                    exact_mass=float(mass_u) / MASS_SCALE,
                    formula=format_formula(counts),
                )
            )
        return out


def format_formula(counts: dict[str, int]) -> str:
    """Строка формулы в порядке :data:`FORMULA_ELEMENT_ORDER` (Hill-подобно)."""
    parts = []
    for el in FORMULA_ELEMENT_ORDER:
        n = int(counts.get(el, 0))
        if n <= 0:
            continue
        parts.append(el if n == 1 else f"{el}{n}")
    return "".join(parts)


__all__ = [
    "FormulaDatabaseReaderV3",
    "SearchResult",
    "format_formula",
    "FORMULA_ELEMENT_ORDER",
    "MASS_U",
    "BIN_WIDTH_U",
    "MASS_SCALE",
]
