import os
from pathlib import Path
import zipfile

import pygrib
import netCDF4 as n4
import mmmpy
# from netCDF4 import Dataset

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
        ds = n4.Dataset(file, mode="r")
        assert isinstance(ds.variables,dict)
        ref = ds.variables["mrefl_mosaic"]
        assert isinstance(ref, n4.Variable)



if __name__ == "__main__":
    bfile = 'data/MREF3D33L_tile1.20140705.145200.gz'
    nfile = 'data/mosaic3d_tile6_20130531-231500.netcdf.zip'    
    ds = n4.Dataset("mosaic3d_tile6_20130531-231500.netcdf")
    tile = mmmpy._read_netcdf(nfile)
    # assert tile.Latitude.max() >= 54 and tile.Latitude.max() <= 55
    # assert tile.Tile == '1'

# def test_read_netcdf():
        # print(ref)
        # print(type(x))
        # print(x.keys())
        # print(ds.variables["mrefl_mosaic"])
        # print(ds.LatGridSpacing)
    # unzip()
    # print(file)
    # x = Path(os.path.abspath(__file__)).parent
    # print(x)
    # ds

    # print(Dataset)
