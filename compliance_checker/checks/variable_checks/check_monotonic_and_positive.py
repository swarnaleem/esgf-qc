import numpy as np
from compliance_checker.base import BaseCheck, TestCtx

def _is_monotonic(arr, mode="increasing", strict=False):
    arr = np.asarray(arr)
    if arr.size < 2:
        return True
    diffs = np.diff(arr)
    if mode == "increasing":
        return np.all(diffs > 0) if strict else np.all(diffs >= 0)
    if mode == "decreasing":
        return np.all(diffs < 0) if strict else np.all(diffs <= 0)
    return True

def check_monotonic_and_positive(ds, var_name, severity=BaseCheck.MEDIUM):
    """
    Enforce monotonicity/positivity when the variable opts into it via attributes:
      - monotonic: one of {'increasing','decreasing','nondecreasing','nonincreasing'}
      - strictly_positive: 'yes' (or boolean True)
    If not declared, the check passes (no-op).
    """
    check_id = "VAR013-014"
    ctx = TestCtx(severity, f"[{check_id}] Monotonic/Positive for '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    v = ds.variables[var_name]
    data = v[...]
    # Handle masked arrays gracefully
    try:
        data = data.compressed()
    except Exception:
        pass

    # 1) monotonic (opt-in)
    mono = getattr(v, "monotonic", "").lower()
    if mono in {"increasing", "decreasing", "nondecreasing", "nonincreasing"}:
        mode = "increasing" if "increasing" in mono else "decreasing"
        strict = mono in {"increasing", "decreasing"}
        if data.ndim > 1:
            # Apply along the leading axis by convention
            data_1d = np.moveaxis(data, 0, -1).reshape(-1, data.shape[0])[:,0]  # fallback: just check along axis 0
        else:
            data_1d = data
        if not _is_monotonic(data_1d, mode=mode, strict=strict):
            ctx.add_failure(f"Values must be {mono} along the primary axis.")
    # 2) strictly positive (opt-in)
    pos_attr = getattr(v, "strictly_positive", None)
    if isinstance(pos_attr, (str, bytes)):
        pos_attr = pos_attr.decode() if isinstance(pos_attr, bytes) else pos_attr
        positive_required = pos_attr.strip().lower() in {"yes", "true", "1"}
    else:
        positive_required = bool(pos_attr)

    if positive_required:
        if not np.all(np.asarray(data) > 0):
            ctx.add_failure("Values must be strictly positive (> 0).")

    if not ctx.msgs:
        ctx.add_pass()

    return [ctx.to_result()]
