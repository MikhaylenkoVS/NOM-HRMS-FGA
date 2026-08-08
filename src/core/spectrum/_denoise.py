"""Denoising + GMM noise threshold."""

import logging
import numpy as np
import math
from dataclasses import dataclass
from typing import Optional
from src.core.domain.spectrum import Spectrum
from src.configs.loader import NOISE_CFG

logger = logging.getLogger(__name__)

# Denoise wrapper (from spectrum_ops.py)


def denoise(
    spec,
    *,
    force=2.0,
    intensity=None,
    quantile=None,
):
    """Remove noise peaks from a spectrum.

    Thin wrapper around ``Spectrum.noise_filter()``.

    Parameters
    ----------
    spec : Spectrum
        Input spectrum.
    force : float, keyword-only, optional
        Multiplier applied to the auto-detected noise level. Default 1.5.
    intensity : float, keyword-only, optional
        Hard absolute intensity threshold. Takes priority when given.
    quantile : float, keyword-only, optional
        Lower intensity quantile in [0, 1]. Used if ``intensity`` is None.

    Returns
    -------
    Spectrum
        Denoised spectrum.

    Notes
    -----
    Parameter priority is ``intensity`` > ``quantile`` > ``force``.
    """
    return spec.noise_filter(force=force, intensity=intensity, quantile=quantile)


# ===========================================================================
# ЭТАП 2b: Назначение брутто-формул
# ===========================================================================

# Default per-element count ranges for brutto assignment.
# Source: pipeline.json -> default_brutto_dict. JSON stores [min, max] lists;


# GMM noise threshold (from noise.py)
def _log_gaussian_pdf(x: np.ndarray, mean: float, var: float) -> np.ndarray:
    """Log-probability density of a 1-D normal distribution."""
    return -0.5 * (np.log(2 * np.pi * var) + (x - mean) ** 2 / var)


def fit_gmm_1d(
    x: np.ndarray,
    n_components: int,
    *,
    max_iter: int = 200,
    tol: float = 1e-4,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Fit a 1-D Gaussian mixture model via EM.

    Parameters
    ----------
    x : np.ndarray, shape (n,)
        Log-transformed intensities.
    n_components : int
        Number of Gaussians in the mixture.
    max_iter : int
        Maximum EM iterations.
    tol : float
        Convergence threshold on log-likelihood change.
    random_state : int
        Seed for reproducible initialisation.

    Returns
    -------
    weights : np.ndarray, shape (K,)
        Mixing coefficients (sum to 1).
    means : np.ndarray, shape (K,)
        Component means.
    vars : np.ndarray, shape (K,)
        Component variances.
    log_likelihood : float
        Final log-likelihood of the data under the fitted model.
    """
    n = len(x)
    K = n_components

    rng = np.random.default_rng(random_state)

    # ── Initialisation (equal-frequency bins) ───────────────────────
    x_sorted = np.sort(x)
    bin_edges = np.linspace(0, n, K + 1, dtype=int)
    means = np.array(
        [np.mean(x_sorted[bin_edges[i] : bin_edges[i + 1]]) for i in range(K)]
    )
    vars = np.ones(K) * np.var(x) * 0.5  # shared initial variance
    weights = np.full(K, 1.0 / K)

    # ── EM loop ─────────────────────────────────────────────────────
    log_likelihood = -np.inf

    for _ in range(max_iter):
        # E-step: responsibilities
        log_resp = np.empty((n, K))
        for k in range(K):
            log_resp[:, k] = np.log(weights[k] + NOISE_CFG.eps) + _log_gaussian_pdf(
                x, means[k], vars[k]
            )

        log_resp_max = log_resp.max(axis=1, keepdims=True)
        resp = np.exp(log_resp - log_resp_max)
        resp_sum = resp.sum(axis=1, keepdims=True)
        resp /= np.maximum(resp_sum, NOISE_CFG.eps)

        # M-step
        Nk = resp.sum(axis=0)
        weights_new = Nk / n
        means_new = np.sum(resp * x[:, np.newaxis], axis=0) / np.maximum(
            Nk, NOISE_CFG.eps
        )
        vars_new = np.zeros(K)
        for k in range(K):
            diff = x - means_new[k]
            vars_new[k] = np.sum(resp[:, k] * diff**2) / max(Nk[k], NOISE_CFG.eps)

        # Regularise: prevent variance collapse
        vars_new = np.maximum(vars_new, 1e-6 * np.var(x))

        means = means_new
        vars = vars_new
        weights = weights_new

        # Log-likelihood
        log_lik = np.sum(
            np.log(np.maximum(resp_sum.flatten(), NOISE_CFG.eps))
        ) + np.sum(log_resp_max)
        if abs(log_lik - log_likelihood) < tol:
            log_likelihood = log_lik
            break
        log_likelihood = log_lik

    return weights, means, vars, log_likelihood


# ===========================================================================
# BIC model selection
# ===========================================================================


def bic(log_likelihood: float, n_params: int, n_samples: int) -> float:
    """Bayesian Information Criterion.

    BIC = -2·log(L) + m·log(n)

    Lower is better.
    """
    return -2.0 * log_likelihood + n_params * np.log(n_samples)


# ===========================================================================
# Gaussian intersection
# ===========================================================================


def gaussian_intersection(
    mu1: float,
    sigma1: float,
    pi1: float,
    mu2: float,
    sigma2: float,
    pi2: float,
) -> float:
    """Find x where two weighted 1-D Gaussians intersect.

    Solves:

        π₁·N(x|μ₁,σ₁²) = π₂·N(x|μ₂,σ₂²)

    which reduces to the quadratic A·x² + B·x + C = 0, with:

        A = 1/(2σ₁²) - 1/(2σ₂²)
        B = μ₂/σ₂² - μ₁/σ₁²
        C = μ₁²/(2σ₁²) - μ₂²/(2σ₂²) - ln(σ₂/σ₁) - ln(π₁/π₂)

    Returns the root that lies between μ₁ and μ₂.
    """
    v1, v2 = sigma1**2, sigma2**2

    A = 1.0 / (2.0 * v1) - 1.0 / (2.0 * v2)
    B = mu2 / v2 - mu1 / v1
    C = (
        (mu1**2) / (2.0 * v1)
        - (mu2**2) / (2.0 * v2)
        - np.log(sigma2 / sigma1)
        - np.log(pi1 / pi2)
    )

    if abs(A) < NOISE_CFG.eps:
        # Degenerate: equal variances → linear equation
        if abs(B) > NOISE_CFG.eps:
            return -C / B
        # Otherwise fall back to midpoint
        return (mu1 + mu2) / 2.0

    disc = B**2 - 4.0 * A * C
    if disc < 0:
        # No real intersection -- return midpoint
        return (mu1 + mu2) / 2.0

    sqrt_disc = np.sqrt(disc)
    x1 = (-B + sqrt_disc) / (2.0 * A)
    x2 = (-B - sqrt_disc) / (2.0 * A)

    # Pick the root between μ₁ and μ₂
    lo, hi = (mu1, mu2) if mu1 < mu2 else (mu2, mu1)
    for xc in (x1, x2):
        if lo <= xc <= hi:
            return xc

    # Neither is between; return the one closer to the midpoint
    mid = (mu1 + mu2) / 2.0
    return x1 if abs(x1 - mid) < abs(x2 - mid) else x2


# ===========================================================================
# Noise threshold result
# ===========================================================================


@dataclass
class NoiseThresholdResult:
    """Result of GMM-based noise threshold detection."""

    threshold: float
    """Intensity threshold in the original (non-log) scale."""

    threshold_log: float
    """Threshold in log10(intensity) space."""

    n_components: int
    """Selected number of Gaussian components (K*)."""

    bic_values: list[float]
    """BIC value for each K = 1 .. max_components."""


# ===========================================================================
# Public API
# ===========================================================================


def compute_noise_threshold(
    intensities: np.ndarray,
    *,
    max_components: int = 15,
    random_state: int = 42,
) -> NoiseThresholdResult:
    """Determine the noise/signal intensity threshold via GMM + BIC.

    Algorithm
    ---------
    1. Log-transform intensities: x = log10(I).
    2. For K = 1 .. max_components, fit a 1-D GMM and record BIC.
    3. Select K* = argmin(BIC).
    4. Find the intersection of the two lowest-mean Gaussians.
    5. Return 10^x_intersection as the intensity threshold.

    Parameters
    ----------
    intensities : np.ndarray
        Array of positive intensity values.
    max_components : int
        Maximum number of Gaussian components to consider.
    random_state : int
        Seed for reproducible GMM initialisation.

    Returns
    -------
    NoiseThresholdResult
    """
    if len(intensities) == 0:
        return NoiseThresholdResult(
            threshold=0.0, threshold_log=-np.inf, n_components=1, bic_values=[]
        )

    # Subsample for performance: GMM on 5 000 points is instant,
    # 500 000 would allocate an n×K matrix (7.5M elements) per EM iteration.
    n_total = len(intensities)
    if n_total > NOISE_CFG.subsample_max_points:
        rng = np.random.default_rng(42)
        idx = rng.choice(n_total, NOISE_CFG.subsample_max_points, replace=False)
        x = np.log10(intensities[idx])
    else:
        x = np.log10(intensities)
    n = len(x)

    bics: list[float] = []
    best_model: tuple | None = None
    best_K: int = 1

    for K in range(1, min(max_components, n) + 1):
        weights, means, vars_arr, log_lik = fit_gmm_1d(x, K, random_state=random_state)
        n_params = K * 3 - 1  # K means + K vars + (K-1) independent weights
        bics.append(bic(log_lik, n_params, n))

        if K == 1 or bics[-1] < bics[best_K - 1]:
            best_K = K
            best_model = (weights, means, vars_arr)

    if best_model is None:
        return NoiseThresholdResult(
            threshold=0.0, threshold_log=-np.inf, n_components=1, bic_values=bics
        )

    weights, means, vars_arr = best_model

    # Sort components by mean (ascending)
    order = np.argsort(means)
    means = means[order]
    vars_arr = vars_arr[order]
    weights = weights[order]

    if best_K == 1:
        # Single component -- use mean as "threshold" (no real noise/signal split)
        x_thr = means[0]
    else:
        mu1, mu2 = means[0], means[1]
        sigma1, sigma2 = np.sqrt(vars_arr[0]), np.sqrt(vars_arr[1])
        pi1, pi2 = weights[0], weights[1]
        x_thr = gaussian_intersection(mu1, sigma1, pi1, mu2, sigma2, pi2)

    thr = 10.0**x_thr
    return NoiseThresholdResult(
        threshold=float(thr),
        threshold_log=float(x_thr),
        n_components=best_K,
        bic_values=[float(v) for v in bics],
    )
