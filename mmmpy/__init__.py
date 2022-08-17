

import zipfile
import shutil
from pathlib import Path
from typing import Callable

import numpy as np
from netCDF4 import Dataset

from .constants import ALTITUDE_SCALE_FACTOR, DEFAULT_VAR, V1_DURATION, V2_DURATION
from ._mmmpy import MosaicDisplay, MosaicGrib, MosaicStitch, MosaicTile, 

__version__ = "2.0.0"

class MosaicTile:
    _label:str =None
    # LatGridSpacing:float
    # LonGridSpacing:float
    def __init__(self, ds:Dataset):
        self.longitude, self.latitude = self._populate_specific_data(ds)
        # self.LatGridSpacing = ds.LatGridSpacing
        # self.LonGridSpacing = ds.LonGridSpacing

    def _populate_specific_data(self) ->tuple[np.ndarray,np.ndarray]:
        return NotImplemented

class MRMSNetCDFV1(MosaicTile):
    _label:str ="mrefl_mosaic"
    def _populate_specific_data(self, ds:Dataset):
        """v1 MRMS netcdf data file"""
        label = self._label
        _, nlat, nlon = ds.variables[label].shape[:3]
        self.StartLat = ds.Latitude
        self.StartLon = ds.Longitude
        self.Height = ds.variables["Height"][:] / ALTITUDE_SCALE_FACTOR
        self.Time = np.float64(ds.Time)
        self.Duration = V1_DURATION
        ScaleFactor = ds.variables[label].Scale
        self.mrefl3d = ds.variables[label][:, :, :] / ScaleFactor
        # Note the subtraction in lat!
        lat = self.StartLat - ds.LatGridSpacing * np.arange(nlat)
        lon = self.StartLon + ds.LonGridSpacing * np.arange(nlon)
        self.Variables = [DEFAULT_VAR]
        return np.meshgrid(lat, lon)

class MRMSNetCDFV2(MosaicTile):
    _label:str ="MREFL"
    def _populate_specific_data(self, ds:Dataset):
        """v2 MRMS netcdf data file"""
        self.Height = ds.variables["Ht"][:] / ALTITUDE_SCALE_FACTOR
        # Getting errors w/ scipy 0.14 when np.array() not invoked below.
        # Think it was not properly converting from scipy netcdf object.
        # v1 worked OK because of the ScaleFactor division in
        self.mrefl3d = np.array(ds.variables[self._label][:, :, :])
        lat = ds.variables["Lat"][:]
        lon = ds.variables["Lon"][:]
        self.StartLat = lat[0]
        self.StartLon = lon[0]
        self.Time = ds.variables["time"][0]
        self.Duration = V2_DURATION
        self.Variables = [DEFAULT_VAR]
        return np.meshgrid(lat, lon)





def unzip(func:Callable):
    tmpdir = Path("/tmp/mmmpy/")

    def __wrapper(filename: Path|str,*args,**kwargs):
        # clear the tmp directory
        if tmpdir.exists():
            shutil.rmtree(tmpdir)
        # create Path object from string
        if isinstance(filename, str):
            filename = Path(filename)
        # validate the file
        if not filename.exists():
            raise FileNotFoundError
        # unzip
        if ".zip" in filename.suffixes:
            with zipfile.ZipFile(filename, "r") as zipref:
                zipref.extractall(tmpdir)
            file, = tmpdir.glob("*")

        return func(file,*args,**kwargs)

    return __wrapper

@unzip
def __read_netcdf(
        filename: Path|str,
        latrange: tuple[float, float] = None,
        lonrange: tuple[float, float] = None,
)->MosaicTile:
    assert isinstance(filename, Path)
    ds = Dataset(filename)
    keys = ds.variables.keys()
    if "mrefl_mosaic" in keys:# version 1
        return MRMSNetCDFV1(ds)
    elif "MREFL" in keys:# version 2
        return MRMSNetCDFV2(ds) 
