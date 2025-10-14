"""
Latitude — dtype must be float (emits V030 on missing var, V031 on wrong dtype).
"""
from compliance_checker.base import BaseCheck, TestCtx
from compliance_checker.checks.utils import find_coord_name, to_array, check_dtype_float

_LAT = ("lat", "latitude")

def check_lat_dtype_float(ds, coord_name="lat", severity=BaseCheck.MEDIUM):
    ctx = TestCtx(severity, f"Latitude dtype check for '{coord_name}'")
    name = find_coord_name(ds, (coord_name,) + _LAT)
    if name is None:
        ctx.add_failure("V030: Latitude coordinate not found (tried: lat, latitude).")
        return [ctx.to_result()]
    arr = to_array(ds.variables[name])
    check_dtype_float(ctx, arr, id_float="V031")
    if not ctx.msgs:
        ctx.add_pass()
    return [ctx.to_result()]
