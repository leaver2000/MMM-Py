from pathlib import Path
from typing import Literal
import xarray as xr


def load(
    ds: xr.Dataset,
    *,
    store: Path = ...,
    vdim: Literal["heightAboveSea"] | None = None,
) -> None:
    """
    load the
    """
    if not vdim:
        raise NotImplementedError

    (dsname,) = ds
    # ##########################
    #          [LOAD]
    # ##########################
    if not store.exists():
        ds.to_zarr(
            store,
            mode="a",
            group=dsname,
            compute=True,
        )
    else:
        ds.drop(["latitude", "longitude", vdim]).to_zarr(
            store,
            mode="a",
            group=dsname,
            append_dim="validTime",
            compute=True,
        )
