__all__ = ["MosaicDisplay", "MosaicGrib", "MosaicStitch"]
import warnings
from pathlib import Path
from typing import Iterable, overload

import numpy as np

# need logic for optioal imports
import dask
import pygrib
import xarray as xr
from netCDF4 import Dataset

from . import use
from ._mmmpy import MosaicDisplay, MosaicGrib, MosaicStitch, MosaicTile
from .constants import ALTITUDE_SCALE_FACTOR, DEFAULT_VAR, V1_DURATION, V2_DURATION

__version__ = "2.0.0"

class MRMSTile:
    _label: str = None
    _mrefl3d:np.ma.MaskedArray
    height:np.ma.MaskedArray
    time:float

    def __init__(self, ds: Dataset):
        self.longitude, self.latitude = self._populate_specific_data(ds)


    def _populate_specific_data(self) -> tuple[np.ndarray, np.ndarray]:
        return NotImplemented
    @property
    def mrefl3d(self)->np.ndarray:
        return self._mrefl3d

class MRMSNetCDFV1(MRMSTile):
    _label: str = "mrefl_mosaic"
    _duration=V1_DURATION
    def _populate_specific_data(self, ds: Dataset):
        """v1 MRMS netcdf data file"""
        label = self._label
        self.height = ds.variables["Height"][:] / ALTITUDE_SCALE_FACTOR

        _, nlat, nlon = ds.variables[label].shape[:3]
        self.StartLat = ds.Latitude
        self.StartLon = ds.Longitude
        self.time = float(ds.Time)
        scale = ds.variables[label].Scale
        self._mrefl3d = ds.variables[label][:, :, :] / scale
        # Note the subtraction in lat!
        lat = self.StartLat - ds.LatGridSpacing * np.arange(nlat)
        lon = self.StartLon + ds.LonGridSpacing * np.arange(nlon)
        self.Variables = [DEFAULT_VAR]
        return np.meshgrid(lat, lon)


class MRMSNetCDFV2(MRMSTile):
    _label: str = "MREFL"
    _duration=V2_DURATION
    def _populate_specific_data(self, ds: Dataset):
        """v2 MRMS netcdf data file"""
        label = self._label
        self.height = ds.variables["Ht"][:] / ALTITUDE_SCALE_FACTOR
        # Getting errors w/ scipy 0.14 when np.array() not invoked below.
        # Think it was not properly converting from scipy netcdf object.
        # v1 worked OK because of the ScaleFactor division in
        self._mrefl3d = np.array(ds.variables[label][:, :, :])
        lat = ds.variables["Lat"][:]
        lon = ds.variables["Lon"][:]
        self.StartLat = lat[0]
        self.StartLon = lon[0]
        self.Time = ds.variables["time"][0]
        self.Variables = [DEFAULT_VAR]
        return np.meshgrid(lat, lon)


def __read_netcdf(
    files: Iterable[Path],
    *,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,
) -> MosaicTile:
    def __generate():
        for file in files:
            ds = Dataset(file)

            keys = ds.variables.keys()

            if "mrefl_mosaic" in keys:  # version 1
                yield MRMSNetCDFV1(ds)

            elif "MREFL" in keys:  # version 2
                yield MRMSNetCDFV2(ds)
            else:
                raise Exception

    return tuple(__generate())




@overload
def read_mrms(
    files: str | Path,
    *,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,
):
    ...

@use.unzip()
def read_mrms(
    files: Iterable[Path],
    filetype: str,
    *,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,
):
    if filetype == "grib":
        ds = xr.open_mfdataset(files, engine="cfgrib", combine="nested", chunks={})
    elif filetype == "netcdf":
        ds = __read_netcdf(files)
    elif filetype == "binary":
        ds = None
    else:
        raise Exception
    return ds
    # print(ds, filetype)
    # xr.open_mfdataset(file)
    # for file in files:
    #     # assert isinstance(file, Path)
    #     try:
    #         if ".netcdf" == file.suffix:
    #             ds = __read_netcdf(file)
    #             print(ds, engine)
    #         if file.suffix.endswith("grib2"):
    #             ds = xr.open_mfdataset(files, engine="cfgrib")
    #             # print(ds)
    #             return
    #             grbs = pygrib.open(file.as_posix())
    #             print(file)
    #             # xr.open_dataset(file)
    #             # print(grbs.read(1))
    #             print(grbs.message(1))
    #             # for grb in grbs:
    #             #     print(grb)
    #             grbs.close()

    #         else:
    #             ...
    #     except:
    #         warnings.warn(
    #             f"FAILED: {file}",
    #         )
