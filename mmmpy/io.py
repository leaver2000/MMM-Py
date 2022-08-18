import warnings
from pathlib import Path
from typing import Iterable, overload


import numpy as np

import xarray as xr
from netCDF4 import Dataset

from . import use
from .core import MRMSDataset


@overload
def read_mrms(
    file: str | Path,
    *,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,
)->MRMSDataset:
    ...


@use.unzip()
def read_mrms(
    files: Iterable[Path],
    filetype: str,
    *,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,
) -> MRMSDataset:
    if filetype == "grib":
        ds = xr.open_mfdataset(
        files,
        engine="cfgrib",
        concat_dim=["heightAboveSea"],
        combine="nested",
        chunks={},
    )
    elif filetype == "netcdf":
        ds = xr.open_mfdataset(files, engine="netcdf4", chunks={})
    elif filetype == "binary":
        ds = None
    else:
        raise Exception

    return MRMSDataset(ds)
