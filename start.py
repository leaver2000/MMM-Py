import os
from pathlib import Path
import zipfile

import pygrib
from netCDF4 import Dataset, Variable
import mmmpy
import xarray as xr

ROOT = Path(os.path.abspath(__file__)).parent

DATA = ROOT / "data"
ARCHIVE = ROOT / "archives"


def unzip():
    file = tuple(DATA.glob("*netcdf*"))[0]
    if not ARCHIVE.exists():
        ARCHIVE.mkdir()
    with zipfile.ZipFile(file, "r") as zip_ref:
        zip_ref.extractall(ARCHIVE)


def use_netcdf4():
    for file in ARCHIVE.glob("*.netcdf"):
        ds = Dataset(file, mode="r")
        assert isinstance(ds.variables, dict)
        ref = ds.variables["mrefl_mosaic"]
        assert isinstance(ref, Variable)


@mmmpy.use.unzip()
def read(filename):
    assert isinstance(filename, Path)
    assert ".zip" not in filename.suffixes
    ...
import numpy as np

if __name__ == "__main__":
    filelist = [
        # MRMS netCDF V1
        "data/mosaic3d_tile6_20130531-231500.netcdf.zip",
        # "data/mrms_binary_data.zip",
        # MRMS grib2
        "data/mrms_grib_data.zip",
    ]
    for file in filelist:
        mrms = mmmpy.read_mrms(file)
        print(mrms)
        # assert isinstance(mrms.height,np.ma.MaskedArray)
        # assert isinstance(mrms.mrefl3d, np.ma.MaskedArray)
