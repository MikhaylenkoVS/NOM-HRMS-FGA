"""Pipeline cache and progress tracking."""
import logging
from typing import Optional
logger = logging.getLogger(__name__)

class PipelineCache:
    """Кэш промежуточных результатов между запусками пайплайна.

    Позволяет не перезагружать спектры и не перевыполнять денойзинг/assign,
    если изменились только параметры более поздних этапов.
    """

    def __init__(self):
        self._loaded: dict[str, object] = {}        # path → Spectrum
        self._denoised: dict[str, object] = {}      # key → Spectrum
        self._assigned: dict[str, object] = {}      # key → Spectrum
        self._series: dict[str, object] = {}        # key → DataFrame

    def _hash(self, *args) -> str:
        return str(hash(args))

    def load(self, path: str, loader, **kw):
        key = f"{path}|{kw.get('sep','')}|{kw.get('mass_min',0)}|{kw.get('mass_max',0)}"
        if key not in self._loaded:
            self._loaded[key] = loader(path, **kw)
        return self._loaded[key]

    def denoise(self, spec, force, intensity, quantile, denoiser):
        key = self._hash(id(spec), force, intensity, quantile)
        if key not in self._denoised:
            self._denoised[key] = denoiser(spec, force=force, intensity=intensity, quantile=quantile)
        return self._denoised[key]

    def assign(self, spec, rel_error_ppm, mass_min, mass_max, search_config, ion_mode, assigner):
        key = self._hash(id(spec), rel_error_ppm, mass_min, mass_max,
                          str(search_config.ranges) if search_config else "", ion_mode)
        if key not in self._assigned:
            self._assigned[key] = assigner(spec, rel_error_ppm=rel_error_ppm,
                                           mass_min=mass_min, mass_max=mass_max,
                                           search_config=search_config, ion_mode=ion_mode)
        return self._assigned[key]

    def series(self, src, deriv, delta, ppm_tol, max_groups, allow_gaps, finder):
        key = self._hash(id(src), id(deriv), delta, ppm_tol, max_groups, allow_gaps)
        if key not in self._series:
            self._series[key] = finder(src, deriv, delta, ppm_tol=ppm_tol,
                                       max_groups=max_groups, allow_gaps=allow_gaps)
        return self._series[key]

    def clear(self):
        self._loaded.clear()
        self._denoised.clear()
        self._assigned.clear()
        self._series.clear()


# Глобальный экземпляр — живёт между вызовами run_pipeline в пределах сессии
_pipeline_cache = PipelineCache()
_result_cache: dict[int, object] = {}


class PipelineProgress:
    """Детальный прогресс пайплайна с шагом 1-2%.

    Диапазоны: загрузка 0-24%, денойзинг 24-48%, assign 48-72%, серии 72-96%, сборка 96-100%.
    """

    def __init__(self, callback):
        self._cb = callback
        self._base = 0
        self._step = 0
        self._total_steps = 0

    def _pct(self, step, total):
        return self._base + int((step / max(total, 1)) * self._range)

    def stage(self, name, base_pct, range_pct):
        self._base = base_pct
        self._range = range_pct
        if self._cb:
            self._cb(f"{name}…", base_pct)

    def tick(self, step, total=None):
        if total is None:
            total = self._total_steps
        self._step = step
        self._total_steps = total
        if self._cb:
            pct = self._pct(step, total)
            self._cb(None, pct)

    def sub(self, name, step, total):
        if self._cb:
            pct = self._pct(step, total)
            self._cb(f"  {name}", pct)

