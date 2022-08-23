from pathlib import Path
import xarray as xr


def load(ds: xr.Dataset, store: Path) -> None:
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
        ds.drop(["latitude", "longitude", "heightAboveSea"]).to_zarr(
            store,
            mode="a",
            group=dsname,
            append_dim="validTime",
            compute=True,
        )
