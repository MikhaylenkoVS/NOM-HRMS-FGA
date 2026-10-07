"""Single import point for project-wide configuration.

Typical usage::

    from src.configs import CHEM, PIPELINE, PATHS

    delta = CHEM.derivatization_shifts["delta_cd3"]
    ppm = PIPELINE.run_pipeline_defaults["ppm_tol"]

Use :func:`load_config` for dynamic access by name.
"""

from src.configs.loader import (
    CHEM,
    CONFIG_DIR,
    FORMULA_SEARCH_CFG,
    ISOTOPE_CFG,
    NOISE_CFG,
    PATHS,
    PIPELINE,
    SPECTRUM_LOAD_CFG,
    ConfigError,
    ConfigNamespace,
    load_config,
)

__all__ = [
    "CHEM",
    "PIPELINE",
    "PATHS",
    "NOISE_CFG",
    "ISOTOPE_CFG",
    "SPECTRUM_LOAD_CFG",
    "FORMULA_SEARCH_CFG",
    "load_config",
    "ConfigNamespace",
    "ConfigError",
    "CONFIG_DIR",
]
