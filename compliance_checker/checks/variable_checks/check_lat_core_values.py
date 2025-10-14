"""
Latitude — core value rules:
- V033: all finite (no NaN/Inf)
- V034: non-decreasing
- V035: unique
- V036: within [-90, 90]
"""
from compliance_checker.base import BaseCheck, TestCtx
from compliance_checker.checks.utils import find_coord_name, to_array, check_core_value_rules

_LAT = ("lat", "latitude")

def check_lat_core_values(ds, coord_name="lat", severity=BaseCheck.MEDIUM):
    ctx = TestCtx(severity, f"Latitude core value checks for '{coord_name}'")
    name = find_coord_name(ds, (coord_name,) + _LAT)
    if name is None:
        ctx.add_failure("V030: Latitude coordinate not found (tried: lat, latitude).")
        return [ctx.to_result()]
    arr = to_array(ds.variables[name])
    ids = {"finite": "V033", "mono": "V034", "uniq": "V035", "range": "V036"}
    check_core_value_rules(ctx, arr, ids, rng=(-90.0, 90.0))
    if not ctx.msgs:
        ctx.add_pass()
    return [ctx.to_result()]
