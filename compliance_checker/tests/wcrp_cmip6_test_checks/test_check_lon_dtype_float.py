import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lon_dtype_float import check_lon_dtype_float

def test_lon_dtype_int_fails(tmp_path):
    p = tmp_path / "lon_dtype.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("x", 3)
        lon = ds.createVariable("lon", "i4", ("x",))
        lon[:] = [0, 10, 20]
    with Dataset(p, "r") as ds:
        res = check_lon_dtype_float(ds, "lon", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V069" in msgs
