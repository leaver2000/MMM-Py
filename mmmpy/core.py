import numpy as np
from numpy.ma import MaskedArray
import xarray as xr


class MRMSDataset:
    def __init__(self, base: xr.Dataset):
        self.__base = base
        # assert isinstance(mrms.height,np.ma.MaskedArray)
        # assert isinstance(mrms.mrefl3d, np.ma.MaskedArray)

    def __repr__(self) -> str:
        return self.to_xarray().__repr__()

    def _repr_html_(self):
        return self.to_xarray()._repr_html_()

    def to_xarray(self) -> xr.Dataset:
        return self.base

    @property
    def base(self):
        return self.__base

    # @property
    # def mrefl3d(self) -> MaskedArray:
    #     return self.base.mrefl3d

    # @property
    # def height(self) -> MaskedArray:
    #     return self.base.height
