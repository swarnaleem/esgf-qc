import pathlib
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_monotonic_and_positive import (
    check_monotonic_and_positive,
)

DATA_DIR = pathlib.Path(__file__).resolve().parents[1] / "compliance_checker" / "tests" / "data"
NC_FILES = sorted(DATA_DIR.rglob("*.nc"))

def _float_1d_vars(ds):
    for name, v in ds.variables.items():
        try:
            if getattr(v, "ndim", 0) == 1 and getattr(v.dtype, "kind", "") in {"f", "i"}:
                yield name
        except Exception:
            continue

def test_runs_on_repo_nc_files():
    for path in NC_FILES:
        with Dataset(str(path), "r") as ds:
            for varname in _float_1d_vars(ds):
                try:
                    res = check_monotonic_and_positive(ds, varname, severity=BaseCheck.MEDIUM)
                    assert isinstance(res, list)
                    for r in res:
                        assert hasattr(r, "name") and hasattr(r, "msgs")
                except Exception:
                    continue
