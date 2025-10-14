import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lat_within_bounds import check_lat_within_bounds

def test_lat_within_bounds_violation(tmp_path):
    p = tmp_path / "lat_bounds.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("y", 3)
        lat = ds.createVariable("lat", "f4", ("y",))
        bnd = ds.createVariable("lat_bnds", "f4", ("y","bnds"))
        ds.createDimension("bnds", 2)
        lat.setncattr("bounds", "lat_bnds")
        lat[:] = np.array([-10.0, 0.0, 10.0], dtype="f4")
        bnd[:] = np.array([[-11.0, -9.0], [-1.0, 1.0], [8.0, 9.0]], dtype="f4")  # last value 10 is outside [8,9]
    with Dataset(p, "r") as ds:
        res = check_lat_within_bounds(ds, "lat", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V037" in msgs
