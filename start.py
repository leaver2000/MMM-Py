import re
import shutil
from pathlib import Path

import numpy as np
import xarray as xr

from typing import Iterable, Hashable

UTC = "UTC"
MAX_TASKS = 5
CFGRIB = "cfgrib"
YYMMDD_HHMMSS = r"(\d{8}-\d{6})"
ACCEPT_HTML = ("accept", "html")
ACCEPT_GZIP = ("accept", "gzip")
TMP_DIR = Path("/tmp/mmmpy/")
datetime64s = "datetime64[s]"
datetime64m = "datetime64[m]"
GRIB2 = "grib2"
FILE_PATTERN = re.compile(r"/([A-Za-z]+(?:-|_)?[A-Za-z]+)+")


def __infer_name_from_file(hist: str) -> Hashable:
    """resolve name from `dataset.attr["history"]`"""
    name_list = FILE_PATTERN.findall(hist)
    if name_list:
        return name_list[-1]
    return "UNABLE_TO_RESOLVE_NAME"


def write_to_store(
    store: Path,
    files: Iterable[Path],
):

    for file in files:

        ds = xr.open_dataset(
            file,
            engine=CFGRIB,
            backend_kwargs=dict(
                mask_and_scale=True,
                decode_times=True,
                concat_characters=True,
                decode_coords=True,
                decode_timedelta=None,
                lock=None,
                indexpath="{path}.{short_hash}.idx",
                filter_by_keys={},
                read_keys=[],
                encode_cf=("parameter", "time", "geography", "vertical"),
                squeeze=True,
                time_dims={"valid_time"},
            ),
        )

        vt, height = (
            ds[key].to_numpy().astype(dtype)
            for key, dtype in (("valid_time", datetime64m), ("heightAboveSea", int))
        )
        if len(ds.data_vars) != 1:
            # mrms grib2 data should only have one variable
            raise Exception
        (ds_name,) = ds
        # not storing history, will use the history object to infer a name
        hist = ds.attrs.pop("history", None)
        # if a name was not explicility provided
        if not name:
            # use the known name if unknow infer one from the file name
            name = ds_name if ds_name != "unknown" else __infer_name_from_file(hist)
        print("writing to zar")

        date = np.datetime_as_string(vt, timezone=UTC)

        date_store = store / f"{date}.zarr"

        append_dim = None

        if date_store.exists():
            append_dim = "heightAboveSea"

        (
            ds.expand_dims({"validTime": [vt], "heightAboveSea": [height]})
            .drop("valid_time")
            .to_zarr(date_store, append_dim=append_dim)
        )


import mmmpy.extract2 as etl
if __name__ == "__main__":
    store = Path(__file__).parent / "data" / "ref3d.zarr"

    etl.main(store)
    # # the path to the data project data directory
    # # root store path
    # store = data / "store"
    # # 
    # if store.exists():
    #     shutil.rmtree(store)

    # store.mkdir(parents=True)

    # write_to_store(
    #     store,
    #     files=(data / "MRMS_MergedReflectivity").glob("*.grib2"),
    # )

    # ds = xr.open_mfdataset(store.rglob("*.zarr"), engine="zarr")

    # print(ds)
    # print(xr.open_zarr(data / "store.zarr" ,consolidated=False))
