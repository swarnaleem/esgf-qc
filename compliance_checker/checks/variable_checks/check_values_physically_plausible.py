import numpy as np
from compliance_checker.base import BaseCheck, TestCtx

def check_values_physically_plausible(ds, var_name, severity=BaseCheck.MEDIUM):
    """
    Use CF-style attributes to validate physical plausibility:
      - valid_min / valid_max / valid_range
      - _FillValue / missing_value handling
    If none of these are provided, the check passes (no-op).
    """
    check_id = "VAR002-006"
    ctx = TestCtx(severity, f"[{check_id}] Physically plausible values for '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    v = ds.variables[var_name]
    try:
        data = v[...]
        # Strip masked values
        data = data.compressed() if hasattr(data, "compressed") else np.asarray(data)
    except Exception as e:
        ctx.add_failure(f"Unable to read data for '{var_name}': {e}")
        return [ctx.to_result()]

    if data.size == 0:
        ctx.add_warning(f"No data to evaluate for '{var_name}'.")
        return [ctx.to_result()]

    # gather declared limits
    vmin = getattr(v, "valid_min", None)
    vmax = getattr(v, "valid_max", None)
    vrng = getattr(v, "valid_range", None)

    # Normalize valid_range
    if vrng is not None and len(vrng) == 2:
        vmin = vrng[0] if vmin is None else max(vmin, vrng[0])
        vmax = vrng[1] if vmax is None else min(vmax, vrng[1])

    finite = np.isfinite(data)
    if not finite.any():
        ctx.add_failure("All values are non-finite (NaN/Inf).")
        return [ctx.to_result()]

    msgs = []
    if vmin is not None:
        below = np.sum(data[finite] < vmin)
        if below:
            msgs.append(f"{below} values below valid_min={vmin}")
    if vmax is not None:
        above = np.sum(data[finite] > vmax)
        if above:
            msgs.append(f"{above} values above valid_max={vmax}")

    if msgs:
        for m in msgs:
            ctx.add_failure(m)
    else:
        ctx.add_pass()

    return [ctx.to_result()]
