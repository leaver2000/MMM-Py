

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from ast import Call

import os
import time
import gzip
import calendar
import datetime
from struct import unpack
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from netCDF4 import Dataset
import six

try:
    import pygrib

    IMPORT_FLAG = True
except ImportError:
    IMPORT_FLAG = False

__version__ = "1.7.0"
VERSION = __version__

# Hard coding of constants
DEFAULT_CLEVS = np.arange(15) * 5.0
DEFAULT_VAR = "mrefl3d"
DEFAULT_VAR_LABEL = "Reflectivity (dBZ)"
V1_DURATION = 300.0  # seconds
V2_DURATION = 120.0  # seconds
ALTITUDE_SCALE_FACTOR = 1_000.0  # Divide meters by this to get something else
DEFAULT_CMAP = cm.GMT_wysiwyg
DEFAULT_PARALLELS = 10  # [20, 37.5, 40, 55]
DEFAULT_MERIDIANS = 10  # [230, 250, 265, 270, 280, 300]
HORIZONTAL_PLOT = [0.1, 0.1, 0.8, 0.8]
VERTICAL_PLOT = [0.1, 0.2, 0.8, 0.8]
THREE_PANEL_SUBPLOT_A = [0.05, 0.10, 0.52, 0.80]
THREE_PANEL_SUBPLOT_B = [0.64, 0.55, 0.33, 0.32]
THREE_PANEL_SUBPLOT_C = [0.64, 0.14, 0.33, 0.32]
DEFAULT_LONLABEL = "Longitude (deg)"
DEFAULT_LATLABEL = "Latitude (deg)"
DEFAULT_ZLABEL = "Height (km MSL)"
DEFAULT_LATRANGE = [20, 55]
DEFAULT_LONRANGE = [-130, -60]
DEFAULT_LINEWIDTH = 0.1

# Following is relevant to MRMS binary format read/write methods
ENDIAN = ""  # Endian currently set automatically by machine type
INTEGER = "i"
DEFAULT_VALUE_SCALE = 10
DEFAULT_DXY_SCALE = 100_000
DEFAULT_Z_SCALE = 1
DEFAULT_MAP_SCALE = 1_000
DEFAULT_MISSING_VALUE = -99
DEFAULT_MRMS_VARNAME = b"mosaicked_refl1     "  # 20 characters
DEFAULT_MRMS_VARUNIT = b"dbz   "  # 6 characters
DEFAULT_FILENAME = "./mrms_binary_file.dat.gz"

# Following is relevant to MRMS grib2 format read/write
BASE_PATH = "/Users/tjlang/Downloads"
TMPDIR = BASE_PATH + "/tmpdir/"
WGRIB2_PATH = BASE_PATH + "/grib2/wgrib2/"
WGRIB2_NAME = "wgrib2"
MRMS_V3_LATRANGE = [20.0, 55.0]
MRMS_V3_LONRANGE = [-130.0, -60.0]

# v1/v2 changeover occurred on 07/30/2013 around 1600 UTC (epoch = 1375200000)
# See 'https://docs.google.com/document/d/' +
# '1Op3uETOtd28YqZffgvEGoIj0qU6VU966iT_QNUOmqn4/edit'
# for details (doc claims 14 UTC, but CSU has v1 data thru 1550 UTC)
V1_TO_V2_CHANGEOVER_EPOCH_TIME = 1_375_200_000
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



from pathlib import Path

import zipfile
import shutil
from typing import Callable

def unzip(func:Callable):
    tmp_mmmpy = Path("/tmp/mmmpy/")

    def __wrapper(filename: Path|str,*args,**kwargs):
        # clear the tmp directory
        if tmp_mmmpy.exists():
            shutil.rmtree(tmp_mmmpy)
        # Path object
        if isinstance(filename, str):
            filename = Path(filename)
        # validate the file
        if not filename.exists():
            raise FileNotFoundError
        # unzip
        if ".zip" in filename.suffixes:
            tmpdir = tmp_mmmpy #/ filename.name.replace(".zip","")
            with zipfile.ZipFile(filename, "r") as zipref:
                zipref.extractall(tmpdir)
            file, = tmpdir.glob("*")

        return func(file,*args,**kwargs)

    return __wrapper

@unzip
def _read_netcdf(
        filename: Path|str,
        keep_nc: bool = True,
        wgrib2_name: bool = WGRIB2_NAME,
        nc_path: bool = TMPDIR,
        latrange: tuple[float, float] = None,
        lonrange: tuple[float, float] = None,
)->MosaicTile:
    assert isinstance(filename, Path)
    ds = Dataset(filename)
    keys = ds.variables.keys()
    if "mrefl_mosaic" in keys:
        # version 1
        label = "mrefl_mosaic"
        return MRMSNetCDFV1(ds)
    elif "MREFL" in keys:
        # version 2
        return MRMSNetCDFV2(ds)
    #     label = "MREFL"
    # nz, nlat, nlon = ds.variables[label].shape[:3]    
    # ds.LatGridSpacing
    # ds.LonGridSpacing
    # print(label)
    # return MosaicTile()
