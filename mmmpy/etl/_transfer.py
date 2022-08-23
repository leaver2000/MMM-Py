"""
transfer
"""
__all__ = ["transfer"]
import re
from pathlib import Path
from typing import Literal
from typing import Iterable

import xarray as xr

FILE_NAME_PATTERN = re.compile(r"/([A-Za-z]+(?:-|_)?[A-Za-z]+)+")
VALID_TIME = "valid_time"


def transfer(
    files: Iterable[Path], vdim: Literal["heightAboveSea"] = None
) -> xr.Dataset:
    """
    ### dimensions:
    - latitude
    - longitude
    - heightAboveSea or None
    - validTime

    files should have only a single temporal and product dimension
    """

    ds = xr.open_mfdataset(
        files,
        chunks={},
        engine="cfgrib",
        data_vars="minimal",
        combine="nested",
        concat_dim=[vdim],
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
            time_dims={VALID_TIME},
        ),
    )
    ds = (
        ds.expand_dims({VALID_TIME: [ds[VALID_TIME].to_numpy()]}).drop_duplicates(
            [VALID_TIME, vdim]
        )
    ).rename({VALID_TIME: "validTime"})

    if len(ds.data_vars) != 1:
        # mrms grib2 data should only have one variable
        raise Exception
    (ds_name,) = ds
    # not storing history, will use the history object to infer a name
    hist = ds.attrs.pop("history", None)
    # if a name was not explicility provided
    # if not name:
    # use the known name if unknow infer one from the file name
    if ds_name != "unknown":
        name = ds_name
    else:
        name_list = FILE_NAME_PATTERN.findall(hist)
        if name_list:
            name = name_list[-1]
        else:
            name = "UNKNOWN"

    return ds.rename({ds_name: name})
