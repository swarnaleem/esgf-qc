import pathlib
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_boundary_variables_existence import (
    check_boundary_variables_existence,
)

DATA_DIR = pathlib.Path(__file__).resolve().parents[1] / "compliance_checker" / "tests" / "data"
NC_FILES = sorted(DATA_DIR.rglob("*.nc"))

def _vars_with_bounds(ds):
    for name, v in ds.variables.items():
        if "bounds" in v.ncattrs():
            yield name

def test_runs_on_repo_nc_files():
    for path in NC_FILES:
        with Dataset(str(path), "r") as ds:
            for varname in _vars_with_bounds(ds):
                res = check_boundary_variables_existence(ds, varname, severity=BaseCheck.MEDIUM)
                assert isinstance(res, list)
                for r in res:
                    assert hasattr(r, "name") and hasattr(r, "msgs")
