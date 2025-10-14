from compliance_checker.base import BaseCheck, TestCtx

def check_boundary_variables_existence(ds, var_name, severity=BaseCheck.MEDIUM):
    """
    For each coordinate used by `var_name`, if that coordinate declares 'bounds',
    the bounds variable must exist and have shape (N, 2).
    """
    check_id = "VAR008"
    ctx = TestCtx(severity, f"[{check_id}] Boundary variables for '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]
    coords = list(var.dimensions)

    any_checked = False
    for c in coords:
        if c not in ds.variables:
            # shape check will flag missing dims elsewhere; warn here
            ctx.add_warning(f"Dimension '{c}' has no corresponding coordinate variable.")
            continue

        cv = ds.variables[c]
        bname = getattr(cv, "bounds", None)
        if not bname:
            continue

        any_checked = True
        if bname not in ds.variables:
            ctx.add_failure(f"Coordinate '{c}' declares bounds '{bname}', but it is missing.")
            continue

        bv = ds.variables[bname]
        if bv.ndim != 2 or bv.shape[1] != 2:
            ctx.add_failure(
                f"Bounds '{bname}' for coord '{c}' must be 2-point intervals; got shape {bv.shape}."
            )

        # First dimension of bounds should match the coordinate length
        if c in cv.dimensions and bv.shape[0] != cv.shape[0]:
            ctx.add_failure(
                f"Bounds '{bname}' length {bv.shape[0]} does not match coordinate '{c}' length {cv.shape[0]}."
            )

    if any_checked and not any("failure" in m for m in ctx._messages_by_severity.values()):
        ctx.add_pass()
    elif not any_checked:
        ctx.add_pass()  # nothing to check is okay

    return [ctx.to_result()]
