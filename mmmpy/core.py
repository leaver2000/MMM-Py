import numpy as np
from numpy.ma import MaskedArray
import pandas as pd
import dask.dataframe as dd
import xarray as xr
from dataclasses import dataclass


@dataclass
class BBox:
    NE: float
    NW: float
    SE: float
    SW: float


class XARRAY_STORE:
    def __init__(self, data: xr.Dataset) -> None:
        self._data = data

    def __repr__(self) -> str:
        return self.to_xarray().__repr__()

    def _repr_html_(self)->str:
        return self.to_xarray()._repr_html_()

    def to_xarray(self) -> xr.Dataset:
        return self.data

    def to_array(self) -> xr.DataArray:
        return self.to_xarray().to_array(dim="variable", name=None)

    def to_pandas(self) -> pd.DataFrame:
        return self.to_xarray().to_pandas()

    def to_dask_dataframe(self) -> dd.DataFrame:
        # dim_order: Sequence[Hashable] | None = None, set_index: bool = False
        return self.to_xarray().to_dask_dataframe()

    @property
    def values(self) -> np.ndarray:
        return self.to_array().values


class MRMSDataset(XARRAY_STORE):
    @property
    def data(self) -> xr.Dataset:
        return super()._data

    @property
    def plot(self) -> "MRMSDisplay":
        return MRMSDisplay(self)

    @property
    def lat(self) -> np.ndarray:
        ...

    @property
    def lon(self) -> np.ndarray:
        ...

    @property
    def lat_range(self) -> np.ndarray:
        ...

    @property
    def lon_range(self) -> np.ndarray:
        ...

    @property
    def bbox(self) -> BBox:
        ...


@dataclass
class MRMSDisplay:
    mrms: MRMSDataset
    """
    not to be instantiated directly
    the display is a plot accessor to the MRMSDataset
    """

    @property
    def data(self) -> xr.Dataset:
        """
        the _data object set by the enherited base class is the
        MRMSDataset, for consisteicy that is overidden to return
        the xarray.dataset
        """
        return self.mrms.to_xarray()  # .to_xarray()

    @property
    def _base(self) -> MRMSDataset:
        return self._data

    @property
    def basemap(self):
        """default map used for plotting"""

    def scatter(self):
        """plot a scatter plot from mrms data"""

    def ref3d(self):
        """3d reflectivity plot"""
