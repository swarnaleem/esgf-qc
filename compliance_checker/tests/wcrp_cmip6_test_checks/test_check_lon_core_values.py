import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lon_core_values import (
    check_lon_core_values,
)

def test_lon_core_values_range_and_monotonic(tmp_path):
    p = tmp_path / "lon_core.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("x", 4)
        lon = ds.createVariable("lon", "f4", ("x",))
        # violate non-decreasing and range [0, 360]
        lon[:] = np.array([0.0, 350.0, 349.0, 361.0], dtype="f4")
    with Dataset(p, "r") as ds:
        res = check_lon_core_values(ds, "lon", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V072" in msgs  # non-decreasing violated
    assert "V074" in msgs  # outside [0, 360]
