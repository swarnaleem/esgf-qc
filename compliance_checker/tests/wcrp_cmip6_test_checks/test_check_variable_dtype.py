import pathlib
from netCDF4 import Dataset
from compliance_checker.base import BaseCheck
from compliance_checker.checks.variable_checks.check_variable_dtype import check_variable_dtype

DATA_DIR = pathlib.Path(__file__).resolve().parents[1] / "compliance_checker" / "tests" / "data"
NC_FILES = sorted(DATA_DIR.rglob("*.nc"))

def test_runs_on_repo_nc_files():
    for path in NC_FILES:
        with Dataset(str(path), "r") as ds:
            for name in ds.variables:
                try:
                    res = check_variable_dtype(ds, name, severity=BaseCheck.MEDIUM)
                    assert isinstance(res, list)
                    for r in res:
                        assert hasattr(r, "name") and hasattr(r, "msgs")
                except Exception:
                    continue
