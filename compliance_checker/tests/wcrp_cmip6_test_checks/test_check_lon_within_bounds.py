import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lon_within_bounds import check_lon_within_bounds

def test_lon_within_bounds_violation(tmp_path):
    p = tmp_path / "lon_bounds.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("x", 3)
        ds.createDimension("bnds", 2)
        lon = ds.createVariable("lon", "f4", ("x",))
        b   = ds.createVariable("lon_bnds", "f4", ("x","bnds"))
        lon.setncattr("bounds", "lon_bnds")
        lon[:] = [5.0, 15.0, 25.0]
        b[:]   = [[0.0, 10.0], [10.0, 20.0], [26.0, 30.0]]  # last value 25 outside [26,30]
    with Dataset(p, "r") as ds:
        res = check_lon_within_bounds(ds, "lon", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V075" in msgs
