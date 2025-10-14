"""
Latitude — each value lies within its corresponding bounds interval (V037).
No-op if bounds are absent/ill-formed (other checks cover presence/shape).
"""
from compliance_checker.base import BaseCheck, TestCtx
from compliance_checker.checks.utils import find_coord_name, to_array, check_within_bounds

_LAT = ("lat", "latitude")

def check_lat_within_bounds(ds, coord_name="lat", severity=BaseCheck.MEDIUM, tol=1e-12):
    ctx = TestCtx(severity, f"Latitude within-bounds check for '{coord_name}'")
    name = find_coord_name(ds, (coord_name,) + _LAT)
    if name is None:
        ctx.add_failure("V030: Latitude coordinate not found (tried: lat, latitude).")
        return [ctx.to_result()]
    v = ds.variables[name]
    bname = getattr(v, "bounds", None)
    if isinstance(bname, (bytes, bytearray)):
        bname = bname.decode("utf-8", "ignore")
    bvar = ds.variables.get(bname) if bname else None
    arr = to_array(v)
    check_within_bounds(ctx, arr, None if bvar is None else bvar[...], id_within="V037", tol=tol)
    if not ctx.msgs:
        ctx.add_pass()
    return [ctx.to_result()]
