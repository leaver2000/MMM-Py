from typing import Hashable
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
    # def __init__(self, data: xr.Dataset) -> None:
    #     self._data = data
    def __init__(self, data: xr.Dataset, name: Hashable) -> None:
        self._data = data
        self._name = name

    def __repr__(self) -> str:
        return self.to_array().__repr__()

    def _repr_html_(self) -> str:
        return self.to_array()._repr_html_()

    def to_xarray(self) -> xr.Dataset:
        return self.data

    def to_array(self) -> xr.DataArray:
        return self.to_xarray().to_array(dim=self._name, name=self._name)

    def to_pandas(self) -> pd.DataFrame:
        return self.to_xarray().to_pandas()

    def to_dask_dataframe(self) -> dd.DataFrame:
        # dim_order: Sequence[Hashable] | None = None, set_index: bool = False
        return self.to_xarray().to_dask_dataframe()

    def to_zarr(self, store, *args, **kwargs):
        return self.data.to_zarr(store, *args, **kwargs)

    @property
    def values(self) -> np.ndarray:
        return self.to_array().values

    @property
    def data(self) -> xr.Dataset:
        return self._data


class MRMSDataset(XARRAY_STORE):
    @property
    def data(self) -> xr.Dataset:
        return super().data

    @property
    def latitude(self) -> xr.DataArray:
        return self.data.latitude

    @property
    def longitude(self) -> xr.DataArray:
        return self.data.longitude

    @property
    def lat_range(self) -> np.ndarray:
        ...

    @property
    def lon_range(self) -> np.ndarray:
        ...

    @property
    def bbox(self) -> "BBox":
        return self.plot.bbox

    @property
    def plot(self) -> "MRMSDisplay":
        return MRMSDisplay(self)


@dataclass
class MRMSDisplay:
    mrms: MRMSDataset
    bbox: BBox = BBox(1, 2, 3, 4)

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
        import cartopy.crs as ccrs

    def verticle(
        self,
        var=bbox,
        lat=None,
        lon=None,
        xrange=None,
        xlabel=None,
        colorbar_flag=True,
        zrange=None,
        # zlabel=DEFAULT_ZLABEL,
        fig=None,
        ax=None,
        # clevs=DEFAULT_CLEVS,
        # cmap=DEFAULT_CMAP,
        title=None,
        save=None,
        verbose=False,
        return_flag=False,
    ):
        """2d verticle reflectivity plot"""

    def horizontal(self):
        """2d horizontal reflectivity plot"""

    def three_panel(
        self,
        # var=DEFAULT_VAR,
        # lat=None,
        # lon=None,
        # latrange=DEFAULT_LATRANGE,
        # lonrange=DEFAULT_LONRANGE,
        # meridians=None,
        # parallels=None,
        # linewidth=DEFAULT_LINEWIDTH,
        # resolution="l",
        # show_grid=True,
        # level=None,
        # area_thresh=10000,
        # lonlabel=DEFAULT_LONLABEL,
        # latlabel=DEFAULT_LATLABEL,
        # zrange=None,
        # zlabel=DEFAULT_ZLABEL,
        # clevs=DEFAULT_CLEVS,
        # cmap=DEFAULT_CMAP,
        title_a=None,
        title_b=None,
        title_c=None,
        xrange_b=None,
        xrange_c=None,
        save=None,
        verbose=False,
        return_flag=False,
        show_crosshairs=True,
    ):
        """
        Plots horizontal and vertical cross-sections through mosaic radar data.
        Subplot (a) is the horizontal view, (b) is the
        var = Variable to be plotted.
        latrange = Desired latitude range of plot (2-element list).
        lonrange = Desired longitude range of plot (2-element list).
        level = If set, performs horizontal cross-section thru that altitude,
                or as close as possible to it. If not set, will plot composite.
        meridians, parallels = Scalars to denote desired gridline spacing.
        linewidth = Width of gridlines (default=0).
        show_grid = Set to False to suppress gridlines and lat/lon tick labels.
        title_a, _b, _c = Strings for subplot titles, None = Basic time & date
                          string as title for subplot (a), and constant lat/lon
                          for (b) and (c). So if you want blank titles use
                          title_?='' as keywords.
        clevs = Desired contour levels.
        cmap = Desired color map.
        save = File to save image to. Careful, PS/EPS/PDF can get large!
        verbose = Set to True if you want a lot of text for debugging.
        zrange = Desired height range of plot (2-element list).
        resolution = Resolution of Basemap instance (e.g., 'c', 'l', 'i', 'h')
        area_thresh = Area threshold to show lakes, etc. (km^2)
        lonlabel, latlabel, zlabel = Axes labels.
        lat/lon = Performs vertical cross-sections thru those lat/lons,
                  or as close as possible to them. Both are required to be set!
        return_flag = Set to True to return plot info.
                      Order is Figure, Axes (3 of them), Basemap.
        show_crosshairs = Set to False to suppress the vertical cross-section
                          crosshairs on the horizontal cross-section.
        xrange_b, _c = Subplot (b) is constant latitude, so xrange_b is is a
                       2-element list that allows the user to adjust the
                       longitude domain of (b). Default lonrange if not set.
                       Similar setup for xrange_c - subplot (c) - except for
                       latitude (i.e., defaults to latrange if not set). The
                       xrange_? variables determine length of crosshairs.
        """
