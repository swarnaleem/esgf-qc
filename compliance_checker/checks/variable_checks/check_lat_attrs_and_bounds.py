"""
Latitude — attributes and bounds metadata:
- axis/standard_name/long_name/units/bounds: existence, type=text, UTF-8, exact values
  (V045–V063)
- bounds variable name/presence/shape/length + legal range (V064 ties into V036)
"""
from compliance_checker.base import BaseCheck, TestCtx
import numpy as np
from compliance_checker.checks.utils import find_coord_name, to_array, utf8_ok

_LAT = ("lat", "latitude")

def check_lat_attrs_and_bounds(ds, coord_name="lat", severity=BaseCheck.MEDIUM):
    ctx = TestCtx(severity, f"Latitude attributes & bounds checks for '{coord_name}'")
    name = find_coord_name(ds, (coord_name,) + _LAT)
    if name is None:
        ctx.add_failure("V030: Latitude coordinate not found (tried: lat, latitude).")
        return [ctx.to_result()]

    v = ds.variables[name]
    expect = {
        "axis": "Y",
        "standard_name": "latitude",
        "long_name": "latitude",
        "units": "degrees_north",
        "bounds": "lat_bnds",
    }
    exist_id = {"axis": "V045", "standard_name": "V049", "long_name": "V053", "units": "V057", "bounds": "V061"}
    type_id  = {"axis": "V046", "standard_name": "V050", "long_name": "V054", "units": "V058", "bounds": "V062"}
    utf8_id  = {"axis": "V047", "standard_name": "V051", "long_name": "V055", "units": "V059", "bounds": "V063"}
    value_id = {"axis": "V048", "standard_name": "V052", "long_name": "V056", "units": "V060", "bounds": "V064"}

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
        if sval != exp and a != "bounds":
            ctx.add_failure(f"{value_id[a]}: '{a}' should be '{exp}', got '{sval}'.")

    bname = getattr(v, "bounds", None)
    if isinstance(bname, (bytes, bytearray)):
        bname = bname.decode("utf-8", "ignore")
    if not bname or bname not in ds.variables:
        ctx.add_failure("V064: Declared bounds variable for latitude missing.")
        return [ctx.to_result()]

    if bname != "lat_bnds":
        ctx.add_failure(f"V064: 'bounds' should be 'lat_bnds'; got '{bname}'.")

    b = ds.variables[bname][...]
    arr = to_array(v)
    if b.ndim != 2 or b.shape[1] != 2:
        ctx.add_failure(f"V064: '{bname}' must have shape (N,2); got {b.shape}.")
    if b.shape[0] != arr.shape[0]:
        ctx.add_failure(f"V064: '{bname}' length {b.shape[0]} != latitude length {arr.shape[0]}.")
    if np.any(b < -90.0) or np.any(b > 90.0):
        ctx.add_failure("V036: Latitude bounds extend outside [-90, 90].")

    if not ctx.msgs:
        ctx.add_pass()
    return [ctx.to_result()]
