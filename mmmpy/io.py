"""module of utility decorator functions"""

import uuid
import gzip
import shutil
import zipfile
from pathlib import Path
from typing import TypeVar, Iterable
from contextlib import contextmanager

import xarray as xr

from .core import MRMSDataset


StrPath = TypeVar("StrPath", str, Path)

ZIP = ".zip"
GZIP = ".gz"
GRIB = "grib"
GRIB2 = "grib2"
NETCDF = "netcdf"
BINARY = "binary"
TMPDIR = f"/tmp/mmmpy-{uuid.uuid1()}/"


def read_mrms(
    files: Iterable[Path],
    filetype: str,
    *,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,
) -> MRMSDataset:
    if filetype == "grib":
        ds = xr.open_mfdataset(
            files,
            chunks={},
            engine="cfgrib",
            concat_dim=["heightAboveSea"],
            combine="nested",
            backend_kwargs=dict(
                mask_and_scale=True,
                decode_times=True,
                concat_characters=True,
                decode_coords=True,
                use_cftime=None,
                decode_timedelta=None,
                lock=None,
                indexpath="{path}.{short_hash}.idx",
                filter_by_keys={},
                read_keys=[],
                encode_cf=("parameter", "time", "geography", "vertical"),
                squeeze=True,
                time_dims=("time", "step"),
            ),
        )
    elif filetype == "netcdf":
        ds = xr.open_mfdataset(
            files,
            engine="netcdf4",
            chunks={},
            backend_kwargs=dict(
                mask_and_scale=True,
                decode_times=True,
                concat_characters=True,
                decode_coords=True,
                use_cftime=None,
                decode_timedelta=None,
                group=None,
                mode="r",
                format="NETCDF4",
                clobber=True,
                diskless=False,
                persist=False,
                lock=None,
                autoclose=False,
            ),
        )
    elif filetype == "binary":
        ds = None
    else:
        raise Exception

    return MRMSDataset(ds)


@contextmanager
def unzip(file: StrPath, tmpdir: StrPath = Path(TMPDIR)):
    """context manager for handling ziped and gziped files"""
    # create path objects
    file, tmpdir = __to_path(file, tmpdir)
    # tmpdir will be deleted, so make sure it doesnt exsist
    assert not tmpdir.exists()
    assert ZIP in file.suffixes
    # make the temp directory
    try:
        tmpdir.mkdir()
        # unzip
        with zipfile.ZipFile(file, "r") as zref:
            # dump every thing into the tmpdir
            zref.extractall(tmpdir)

        yield __iterfiles(tmpdir)
    finally:
        shutil.rmtree(tmpdir)

def __to_path(*args: StrPath):
    """converts str to Path objects"""
    for arg in args:
        if isinstance(arg, str):
            yield Path(arg)
        else:
            yield arg


def __iterfiles(tmpdir: StrPath) -> Iterable[Path]:
    for file in tmpdir.glob("*"):
        # handle any gziped files
        if GZIP in file.suffixes:
            with gzip.open(file, "rb") as zref:
                file = tmpdir / file.name.removesuffix(".gz")
                with file.open("wb") as fout:
                    shutil.copyfileobj(zref, fout)
        yield file

