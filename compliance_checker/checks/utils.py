"""
Utilities for CMIP7 latitude/longitude coordinate checks.

This module contains small, reusable helpers used by the per-ID check files.
It does NOT emit any check IDs itself; callers (the per-ID modules) pass the
exact CSV ID strings into these helpers when composing messages.

Provided utilities
------------------
Name resolution & array access
- find_coord_name(ds, candidates) -> str|None
- to_array(var) -> np.ndarray
- utf8_ok(value) -> bool

Core assertions (ID emitted by caller)
- check_dtype_float(ctx, arr, id_float)
- check_core_value_rules(ctx, arr, ids, rng)
  * ids = {"finite": V-id, "mono": V-id, "uniq": V-id, "range": V-id}
  * rng = (min_allowed, max_allowed)
- check_within_bounds(ctx, arr, bnds, id_within, tol=1e-12)

Optional extras (helpers for non-mandatory checks; no IDs here)
- contiguous_nonoverlapping(bounds, atol=1e-8) -> (ok, reason)
- bounds_cover_extent(bounds, coord, atol=1e-8) -> bool
- midpoint_matches(bounds, coord, rtol=0.0, atol=1e-8) -> bool
- normalize_lon0360(lon) -> np.ndarray
- is_cyclic_lon(lon, bounds=None, atol=1e-6) -> bool
"""

from __future__ import annotations
import numpy as np


# ---------- name resolution & basic IO ----------

def find_coord_name(ds, candidates):
    """Return the first candidate name present in ds.variables, else None."""
    for n in candidates:
        if n in ds.variables:
            return n
    return None


def to_array(var):
    """Return a NumPy array view of a netCDF/xarray variable, stripping masks if present."""
    a = var[...]
    return a.compressed() if hasattr(a, "compressed") else np.asarray(a)


def utf8_ok(v) -> bool:
    """True if the given attribute value can round-trip as UTF-8 text."""
    try:
        s = v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else str(v)
        s.encode("utf-8")
        return True
    except Exception:
        return False


# ---------- core assertions (caller supplies CSV IDs) ----------

def check_dtype_float(ctx, arr, id_float: str):
    """Fail on ctx if `arr` is not floating-point. Uses the provided CSV ID in the message."""
    kind = getattr(arr, "dtype", None).kind if hasattr(arr, "dtype") else None
    if kind != "f":
        ctx.add_failure(f"{id_float}: dtype must be floating-point (NC_FLOAT); got kind '{kind}'.")


def check_core_value_rules(ctx, arr, ids: dict, rng: tuple[float, float]):
    """
    Apply the common coordinate rules:
      - all finite
      - non-decreasing
      - unique
      - within allowed range [rng[0], rng[1]]
    Messages use the CSV IDs provided via `ids`.
    Example ids: {"finite":"V033","mono":"V034","uniq":"V035","range":"V036"}
    """
    # finite
    if not np.all(np.isfinite(arr)):
        ctx.add_failure(f"{ids['finite']}: contains NaN or Inf values.")

    # monotonic non-decreasing
    if arr.size >= 2 and not np.all(np.diff(arr) >= 0):
        ctx.add_failure(f"{ids['mono']}: values must be non-decreasing.")

    # unique
    if np.unique(arr).size != arr.size:
        ctx.add_failure(f"{ids['uniq']}: values must be unique (no duplicates).")

    # range
    lo, hi = float(rng[0]), float(rng[1])
    below = int(np.sum(arr < lo))
    above = int(np.sum(arr > hi))
    if below or above:
        ctx.add_failure(f"{ids['range']}: values out of range [{lo}, {hi}] (below={below}, above={above}).")


def check_within_bounds(ctx, arr, bnds, id_within: str, tol: float = 1e-12):
    """
    If bounds are provided and well-formed, ensure coord[i] ∈ [lower[i], upper[i]] (±tol).
    Uses `id_within` in failure messages. Does nothing if bnds is None or ill-formed.
    """
    if bnds is None:
        return
    b = np.asarray(bnds, dtype=float)
    if b.ndim != 2 or b.shape[1] != 2 or b.shape[0] != arr.shape[0]:
        return  # another check should handle shape/length
    lower, upper = b[:, 0], b[:, 1]
    outside = (arr < (lower - tol)) | (arr > (upper + tol))
    if np.any(outside):
        n = int(np.sum(outside))
        ctx.add_failure(f"{id_within}: {n} values lie outside their declared bounds.")


# ---------- optional extras for non-mandatory niceties ----------

def contiguous_nonoverlapping(bounds, atol: float = 1e-8) -> tuple[bool, str]:
    """Check that consecutive intervals are touching (no gaps) and non-overlapping."""
    b = np.asarray(bounds, dtype=float)
    lower, upper = b[:, 0], b[:, 1]
    if np.any(upper < lower - atol):
        return False, "Some intervals have upper < lower."
    dif = lower[1:] - upper[:-1]
    if np.any(dif > atol):
        return False, "Gaps exist between consecutive intervals."
    if np.any(dif < -atol):
        return False, "Overlaps exist between consecutive intervals."
    return True, ""


def bounds_cover_extent(bounds, coord, atol: float = 1e-8) -> bool:
    """True if first lower == min(coord) and last upper == max(coord) within tolerance."""
    b = np.asarray(bounds, dtype=float)
    c = np.asarray(coord, dtype=float)
    return (abs(b[0, 0] - np.min(c)) <= atol) and (abs(b[-1, 1] - np.max(c)) <= atol)


def midpoint_matches(bounds, coord, rtol: float = 0.0, atol: float = 1e-8) -> bool:
    """True if coord values equal the midpoint of their bounds within tolerance."""
    b = np.asarray(bounds, dtype=float)
    c = np.asarray(coord, dtype=float)
    mid = 0.5 * (b[:, 0] + b[:, 1])
    return np.allclose(c, mid, rtol=rtol, atol=atol)


def normalize_lon0360(lon):
    """Normalize longitude array to [0, 360) by modulo operation. Returns a new ndarray."""
    lon = np.asarray(lon, dtype=float)
    return np.mod(lon, 360.0)


def is_cyclic_lon(lon, bounds=None, atol: float = 1e-6) -> bool:
    """
    Heuristic to detect cyclic longitudes (global wrap at 360 degrees).
    True if either:
      - differences show a large negative jump (e.g., ~360→0), or
      - last bound upper ≈ first bound lower + 360 (if bounds provided).
    """
    l = np.asarray(lon, dtype=float)
    if l.size > 1 and np.any(np.diff(l) < -180.0):
        return True
    if bounds is not None:
        b = np.asarray(bounds, dtype=float)
        if b.ndim == 2 and b.shape[1] == 2:
            return abs(b[-1, 1] - (b[0, 0] + 360.0)) <= atol
    return False
