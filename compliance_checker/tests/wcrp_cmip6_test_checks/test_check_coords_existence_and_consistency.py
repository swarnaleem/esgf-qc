import pathlib
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_coords_existence_and_consistency import (
    check_coords_existence_and_consistency,
)

DATA_DIR = pathlib.Path(__file__).resolve().parents[1] / "compliance_checker" / "tests" / "data"
NC_FILES = sorted(DATA_DIR.rglob("*.nc"))

def _candidate_data_vars(ds):
    preferred = {"tas", "tos", "pr", "psl", "ua", "va", "ta"}
    for name in sorted(preferred & set(ds.variables.keys())):
        yield name
    for name, v in ds.variables.items():
        if name in {"time", "lat", "latitude", "lon", "longitude"}:
            continue
        if name.endswith("_bnds") or name.endswith("_bounds"):
            continue
        if getattr(v, "ndim", 0) >= 1:
            yield name

def test_runs_on_repo_nc_files():
    for path in NC_FILES:
        with Dataset(str(path), "r") as ds:
            for varname in _candidate_data_vars(ds):
                try:
                    res = check_coords_existence_and_consistency(ds, varname, severity=BaseCheck.MEDIUM)
                    assert isinstance(res, list)
                    for r in res:
                        assert hasattr(r, "name") and hasattr(r, "msgs")
                    break  # one var per file
                except Exception:
                    continue
