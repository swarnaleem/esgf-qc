import numpy as np
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_lat_core_values import check_lat_core_values

def test_lat_core_values_basic_failures(tmp_path):
    p = tmp_path / "lat_core.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("y", 4)
        lat = ds.createVariable("lat", "f4", ("y",))
        lat[:] = np.array([-95.0, -10.0, -10.0, 5.0], dtype="f4")  # out-of-range, duplicate (not unique), non-decreasing OK
    with Dataset(p, "r") as ds:
        res = check_lat_core_values(ds, "lat", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V033" not in msgs  # finite
    assert "V034" not in msgs  # non-decreasing
    assert "V035" in msgs      # unique violated
    assert "V036" in msgs      # [-90,90] violated

def test_lat_core_values_monotonic_fail(tmp_path):
    p = tmp_path / "lat_core_monot.nc"
    with Dataset(p, "w") as ds:
        ds.createDimension("y", 3)
        lat = ds.createVariable("lat", "f4", ("y",))
        lat[:] = [0.0, 5.0, 2.0]  # not non-decreasing
    with Dataset(p, "r") as ds:
        res = check_lat_core_values(ds, "lat", severity=BaseCheck.MEDIUM)
    msgs = "\n".join(m for r in res for m in r.msgs)
    assert "V034" in msgs
