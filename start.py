# from pathlib import Path
# import uuid
# import xarray as xr
# from mmmpy._async import grib2zarr
# import zarr
# import numpy as np

# datetime64m = "datetime64[m]"
# UTC = "UTC"
# CFGRIB="cfgrib"

# def open_dataset(file: Path, store: Path) -> None:

#     ds = xr.open_dataset(
#         file,
#         engine=CFGRIB,
#         backend_kwargs=dict(
#             mask_and_scale=True,
#             decode_times=True,
#             concat_characters=True,
#             decode_coords=True,
#             decode_timedelta=None,
#             lock=None,
#             indexpath="{path}.{short_hash}.idx",
#             filter_by_keys={},
#             read_keys=[],
#             encode_cf=("parameter", "time", "geography", "vertical"),
#             squeeze=True,
#             time_dims={"valid_time"},
#         ),
#     )

#     vt, height = (
#         ds[key].to_numpy().astype(dtype)
#         for key, dtype in (("valid_time", datetime64m), ("heightAboveSea", int))
#     )

#     path = f"{np.datetime_as_string(vt,timezone=UTC)}/{height}"

#     res = (
#         ds.expand_dims({"validTime": [vt], "heightAboveSea": [height]})
#         .drop("valid_time")
#         .to_zarr(store=zarr.DirectoryStore(store / path), mode="a")
#     )
#     print(res)

from mmmpy.extract2 import main
from pathlib import Path

if __name__ == "__main__":

    #     # path to data directory
    data = Path(__file__).parent / "data" / "MRMS_MergedReflectivity.zarr"
    main(data)
#     # directory of gribfiles
#     mref = data / "MRMS_MergedReflectivity"
#     # path to zarr storage
#     store = data / f"{uuid.uuid1()}.zarr"
#     # loop all of the grib2 files
#     for file in mref.glob("*.grib2"):
#         open_dataset(file, store)
