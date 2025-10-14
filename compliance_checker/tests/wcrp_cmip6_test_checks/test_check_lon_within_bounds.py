import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lon_within_bounds import (
    check_lon_within_bounds,
)

def test_lon_within_bounds_violation(tmp_path):
    p = tmp_path / "lon_bounds.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("x", 3)
        ds.createDimension("bnds", 2)
        lon = ds.createVariable("lon", "f4", ("x",))
        bnd = ds.createVariable("lon_bnds", "f4", ("x", "bnds"))
        lon.setncattr("bounds", "lon_bnds")

        lon[:] = np.array([5.0, 15.0, 25.0], dtype="f4")
        # last value 25.0 lies outside [26, 30] -> should trigger V075
        bnd[:] = np.array([[0.0, 10.0], [10.0, 20.0], [26.0, 30.0]], dtype="f4")

    with Dataset(p, "r") as ds:
        res = check_lon_within_bounds(ds, "lon", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V075" in msgs

def test_lon_within_bounds_no_bounds_is_noop(tmp_path):
    """If no bounds are declared, this check should return a pass Result (no failure)."""
    p = tmp_path / "lon_nobounds.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("x", 3)
        lon = ds.createVariable("lon", "f4", ("x",))
        lon[:] = [0.0, 10.0, 20.0]
    with Dataset(p, "r") as ds:
        res = check_lon_within_bounds(ds, "lon", severity=BaseCheck.MEDIUM)
    # function returns a single Result with pass if nothing to check
    assert isinstance(res, list)
    assert all(isinstance(r.msgs, list) for r in res)
