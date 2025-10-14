"""
Longitude — attributes and bounds metadata:
- axis/standard_name/long_name/units/bounds: existence, type=text, UTF-8, exact values
  (V083–V101)
- bounds variable name/presence/shape/length + legal range (V102 ties into V074)
"""
from compliance_checker.base import BaseCheck, TestCtx
import numpy as np
from compliance_checker.checks.utils import find_coord_name, to_array, utf8_ok

_LON = ("lon", "longitude")

def check_lon_attrs_and_bounds(ds, coord_name="lon", severity=BaseCheck.MEDIUM):
    ctx = TestCtx(severity, f"Longitude attributes & bounds checks for '{coord_name}'")
    name = find_coord_name(ds, (coord_name,) + _LON)
    if name is None:
        ctx.add_failure("V068: Longitude coordinate not found (tried: lon, longitude).")
        return [ctx.to_result()]

    v = ds.variables[name]
    expect = {
        "axis": "X",
        "standard_name": "longitude",
        "long_name": "longitude",
        "units": "degrees_east",
        "bounds": "lon_bnds",
    }
    exist_id = {"axis": "V083", "standard_name": "V087", "long_name": "V091", "units": "V095", "bounds": "V099"}
    type_id  = {"axis": "V084", "standard_name": "V088", "long_name": "V092", "units": "V096", "bounds": "V100"}
    utf8_id  = {"axis": "V085", "standard_name": "V089", "long_name": "V093", "units": "V097", "bounds": "V101"}
    value_id = {"axis": "V086", "standard_name": "V090", "long_name": "V094", "units": "V098"}

    for a, exp in expect.items():
        if not hasattr(v, a):
            ctx.add_failure(f"{exist_id[a]}: Missing attribute '{a}'.")
            continue
        val = getattr(v, a)
        if not isinstance(val, (str, bytes, bytearray)):
            ctx.add_failure(f"{type_id[a]}: Attribute '{a}' must be text.")
        if not utf8_ok(val):
            ctx.add_failure(f"{utf8_id[a]}: Attribute '{a}' not UTF-8 encodable.")
        sval = val.decode("utf-8", "ignore") if isinstance(val, (bytes, bytearray)) else str(val)
        if a != "bounds" and sval != exp:
            ctx.add_failure(f"{value_id[a]}: '{a}' should be '{exp}', got '{sval}'.")

    bname = getattr(v, "bounds", None)
    if isinstance(bname, (bytes, bytearray)):
        bname = bname.decode("utf-8", "ignore")
    if not bname or bname not in ds.variables:
        ctx.add_failure("V102: Declared bounds variable for longitude missing.")
        return [ctx.to_result()]

    if bname != "lon_bnds":
        ctx.add_failure(f"V102: 'bounds' should be 'lon_bnds'; got '{bname}'.")

    b = ds.variables[bname][...]
    arr = to_array(v)
    if b.ndim != 2 or b.shape[1] != 2:
        ctx.add_failure(f"V102: '{bname}' must have shape (N,2); got {b.shape}.")
    if b.shape[0] != arr.shape[0]:
        ctx.add_failure(f"V102: '{bname}' length {b.shape[0]} != longitude length {arr.shape[0]}.")
    if np.any(b < 0.0) or np.any(b > 360.0):
        ctx.add_failure("V074: Longitude bounds extend outside [0, 360].")

    if not ctx.msgs:
        ctx.add_pass()
    return [ctx.to_result()]
