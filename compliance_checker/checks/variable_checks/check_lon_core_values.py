"""
Longitude — each value lies within its corresponding bounds interval (V075).
No-op if bounds are absent/ill-formed (other checks cover presence/shape).
"""
from compliance_checker.base import BaseCheck, TestCtx
from compliance_checker.checks.utils import find_coord_name, to_array, check_within_bounds

_LON = ("lon", "longitude")

def check_lon_within_bounds(ds, coord_name="lon", severity=BaseCheck.MEDIUM, tol=1e-12):
    ctx = TestCtx(severity, f"Longitude within-bounds check for '{coord_name}'")
    name = find_coord_name(ds, (coord_name,) + _LON)
    if name is None:
        ctx.add_failure("V068: Longitude coordinate not found (tried: lon, longitude).")
        return [ctx.to_result()]
    v = ds.variables[name]
    bname = getattr(v, "bounds", None)
    if isinstance(bname, (bytes, bytearray)):
        bname = bname.decode("utf-8", "ignore")
    bvar = ds.variables.get(bname) if bname else None
    arr = to_array(v)
    check_within_bounds(ctx, arr, None if bvar is None else bvar[...], id_within="V075", tol=tol)
    if not ctx.msgs:
        ctx.add_pass()
    return [ctx.to_result()]
