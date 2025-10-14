import numpy as np
from compliance_checker.base import BaseCheck, TestCtx

def check_variable_dtype(ds, var_name, severity=BaseCheck.MEDIUM):
    """
    Ensure data variables are numeric. String/object dtypes are only allowed when
    clearly marked as identifiers (e.g., cf_role, flag_meanings).
    """
    check_id = "VAR011"
    ctx = TestCtx(severity, f"[{check_id}] Dtype check for '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    v = ds.variables[var_name]
    kind = getattr(v[:], "dtype", getattr(v, "dtype", None)).kind if hasattr(v, "dtype") else v.dtype.kind  # xarray/netCDF4 tolerant

    # allow numeric kinds
    if kind in ("f", "i", "u"):
        ctx.add_pass()
        return [ctx.to_result()]

    # allow strings only for specific metadata roles
    if kind in ("S", "U"):
        # If it's a coordinate id or feature id, allow; else warn.
        role = getattr(v, "cf_role", "").lower()
        if role in {"timeseries_id", "profile_id", "trajectory_id"}:
            ctx.add_pass()
        else:
            # flags may be split across attributes
            if hasattr(v, "flag_meanings") or hasattr(v, "flag_values"):
                ctx.add_pass()
            else:
                ctx.add_warning(f"Non-numeric dtype for '{var_name}' (kind '{kind}') may not be CF-compliant.")
        return [ctx.to_result()]

    # anything else is a failure
    ctx.add_failure(f"Unsupported dtype kind '{kind}' for '{var_name}'. Expected numeric or CF-allowed string.")
    return [ctx.to_result()]
