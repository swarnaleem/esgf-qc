"""
Longitude — dtype must be float (emits V068 on missing var, V069 on wrong dtype).
"""
from compliance_checker.base import BaseCheck, TestCtx
from compliance_checker.checks.utils import find_coord_name, to_array, check_dtype_float

_LON = ("lon", "longitude")

def check_lon_dtype_float(ds, coord_name="lon", severity=BaseCheck.MEDIUM):
    ctx = TestCtx(severity, f"Longitude dtype check for '{coord_name}'")
    name = find_coord_name(ds, (coord_name,) + _LON)
    if name is None:
        ctx.add_failure("V068: Longitude coordinate not found (tried: lon, longitude).")
        return [ctx.to_result()]
    arr = to_array(ds.variables[name])
    check_dtype_float(ctx, arr, id_float="V069")
    if not ctx.msgs:
        ctx.add_pass()
    return [ctx.to_result()]
