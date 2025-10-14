import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lon_attrs_and_bounds import check_lon_attrs_and_bounds

def _mk_ok(ds):
    ds.createDimension("x", 3)
    ds.createDimension("bnds", 2)
    lon = ds.createVariable("lon", "f4", ("x",))
    b = ds.createVariable("lon_bnds", "f4", ("x","bnds"))
    lon.setncattr("axis", "X")
    lon.setncattr("standard_name", "longitude")
    lon.setncattr("long_name", "longitude")
    lon.setncattr("units", "degrees_east")
    lon.setncattr("bounds", "lon_bnds")
    lon[:] = [0.0, 10.0, 20.0]
    b[:]   = [[-1.0, 1.0], [9.0, 11.0], [19.0, 21.0]]

def test_lon_attrs_wrong_axis_emits_id(tmp_path):
    p = tmp_path / "lon_attrs_axis.nc"
    with Dataset(p, "w") as ds:
        _mk_ok(ds)
        ds.variables["lon"].setncattr("axis", "Y")  # wrong
    with Dataset(p, "r") as ds:
        res = check_lon_attrs_and_bounds(ds, "lon", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V086" in msgs  # exact value mismatch for axis

def test_lon_bounds_outside_range_emits_id(tmp_path):
    p = tmp_path / "lon_bounds_range.nc"
    with Dataset(p, "w") as ds:
        _mk_ok(ds)
        ds.variables["lon_bnds"][:] = [[-5.0, 1.0], [9.0, 11.0], [19.0, 400.0]]  # outside [0, 360]
    with Dataset(p, "r") as ds:
        res = check_lon_attrs_and_bounds(ds, "lon", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V074" in msgs  # bounds extend outside legal lon range
