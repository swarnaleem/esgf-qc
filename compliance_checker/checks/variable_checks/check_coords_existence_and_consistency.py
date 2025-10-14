from compliance_checker.base import BaseCheck, TestCtx

_CF_COORD_NAMES = {"time", "lat", "latitude", "lon", "longitude", "lev", "level", "depth", "height"}

def _has_attr(v, name):
    try:
        getattr(v, name)
        return True
    except AttributeError:
        return False

def check_coords_existence_and_consistency(ds, var_name, severity=BaseCheck.MEDIUM):
    """
    Ensure required coordinate variables exist for `var_name`, and that common
    CF attributes are present when applicable (units/standard_name/axis).
    """
    check_id = "VAR007"
    ctx = TestCtx(severity, f"[{check_id}] Coordinate variables for '{var_name}'")

    if var_name not in ds.variables:
        ctx.add_failure(f"Variable '{var_name}' not found in dataset.")
        return [ctx.to_result()]

    var = ds.variables[var_name]

    # 1) coordinates declared via 'coordinates' attribute
    declared = []
    coords_attr = getattr(var, "coordinates", None)
    if coords_attr:
        declared = [c for c in coords_attr.split() if c]

    # 2) infer from dimension names (common CF names)
    inferred = [d for d in var.dimensions if d in ds.variables and d in _CF_COORD_NAMES]

    coord_names = list(dict.fromkeys(declared + inferred))  # unique, keep order

    missing = [c for c in coord_names if c not in ds.variables]
    if missing:
        ctx.add_failure(f"Missing coordinate variables: {missing}")

    # light attribute sanity for any present coords
    for c in coord_names:
        if c not in ds.variables:
            continue
        cv = ds.variables[c]
        # If it looks like a coordinate, encourage key attrs
        attr_gaps = []
        if not _has_attr(cv, "units"):
            attr_gaps.append("units")
        if not _has_attr(cv, "standard_name"):
            attr_gaps.append("standard_name")
        # axis is optional but helpful for CF
        if not _has_attr(cv, "axis"):
            attr_gaps.append("axis")
        if attr_gaps:
            ctx.add_warning(f"Coordinate '{c}' is missing attrs: {', '.join(attr_gaps)}")

    if not ctx.msgs:
        ctx.add_pass()

    return [ctx.to_result()]
