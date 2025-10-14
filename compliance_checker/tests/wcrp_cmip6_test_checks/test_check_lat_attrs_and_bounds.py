import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lat_attrs_and_bounds import check_lat_attrs_and_bounds

def _mk_ok(ds):
    ds.createDimension("y", 3)
    ds.createDimension("bnds", 2)
    lat = ds.createVariable("lat", "f4", ("y",))
    b = ds.createVariable("lat_bnds", "f4", ("y","bnds"))
    lat.setncattr("axis", "Y")
    lat.setncattr("standard_name", "latitude")
    lat.setncattr("long_name", "latitude")
    lat.setncattr("units", "degrees_north")
    lat.setncattr("bounds", "lat_bnds")
    lat[:] = [-10.0, 0.0, 10.0]
    b[:] = [[-11.0, -9.0], [-1.0, 1.0], [9.0, 11.0]]

def test_lat_attrs_units_mismatch_emits_id(tmp_path):
    p = tmp_path / "lat_attrs.nc"
    with Dataset(p, "w") as ds:
        _mk_ok(ds)
        # break units
        ds.variables["lat"].setncattr("units", "degree_north")
    with Dataset(p, "r") as ds:
        res = check_lat_attrs_and_bounds(ds, "lat", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V060" in msgs  # units exact value mismatch

def test_lat_attrs_bounds_presence_and_shape(tmp_path):
    p = tmp_path / "lat_bounds_shape.nc"
    with Dataset(p, "w") as ds:
        _mk_ok(ds)
        # break shape to (3,3)
        ds.variables["lat_bnds"][:] = [[-11,-9,0],[-1,1,0],[9,11,0]]
    with Dataset(p, "r") as ds:
        res = check_lat_attrs_and_bounds(ds, "lat", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V064" in msgs  # bounds shape/length failure
