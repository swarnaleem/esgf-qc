import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lat_dtype_float import check_lat_dtype_float

def _mk_nc(tmp_path, dtype):
    p = tmp_path / "lat_dtype.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("y", 3)
        lat = ds.createVariable("lat", dtype, ("y",))
        lat[:] = np.array([0, 10, 20], dtype=dtype)
    return p

def test_lat_dtype_passes_with_float(tmp_path):
    p = _mk_nc(tmp_path, "f4")
    with Dataset(p, "r") as ds:
        res = check_lat_dtype_float(ds, "lat", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V031" not in msgs  # no dtype failure

def test_lat_dtype_fails_with_int(tmp_path):
    p = _mk_nc(tmp_path, "i4")
    with Dataset(p, "r") as ds:
        res = check_lat_dtype_float(ds, "lat", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V031" in msgs
