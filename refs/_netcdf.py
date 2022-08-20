__all__ =["MRMSTile", "MRMSNetCDFV1", "MRMSNetCDFV2"]

import numpy as np
from netCDF4 import Dataset

from .constants import ALTITUDE_SCALE_FACTOR, V1_DURATION, V2_DURATION, DEFAULT_VAR

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
