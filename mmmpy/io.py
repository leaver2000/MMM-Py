"""module of utility decorator functions"""

import uuid
import gzip
import shutil
import zipfile
from pathlib import Path
from typing import TypeVar, Iterable, Literal
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


BACKEND = {
    "cfgrib": {
        "concat_dim": ["heightAboveSea"],
        "backend_kwargs": dict(
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
    },
    "netcdf4": {
        "concat_dim": ["Ht"],
        "backend_kwargs": dict(
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
    },
}
RENAME ={
    "netcdf4":{"Ht":"heightAboveSea", "Lat":"latitude", "Lon":'longitude' },
    "cfgrib":{}
}
Engine = Literal["netcdf4", "cfgrib", "binary"]

def __backend(engine: Engine, *, filter_by_keys=None):
    return BACKEND[engine]


def read_mrms(
    files: Iterable[Path],
    *,
    engine: Engine = None,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,

) -> MRMSDataset:
    if engine not in ["netcdf4", "cfgrib", "binary"]:
        raise Exception

    elif engine != "binary":
        ds = xr.open_mfdataset(
            tuple(files)[:2],
            chunks={},
            engine=engine,
            combine="nested",
            **__backend(engine, filter_by_keys={})
            # backend_kwargs=__backend(engine, filter_by_keys={})
        ).rename(RENAME[engine])
    else:
        ds = None

    return MRMSDataset(ds)


@contextmanager
def unzip(file: StrPath, tmpdir: StrPath = Path(TMPDIR)):
    """context manager for handling ziped and gziped files"""
    # create path objects
    file, tmpdir = __to_path(file, tmpdir)
    # tmpdir will be deleted, so make sure it doesnt exsist
    assert not tmpdir.exists()
    # if not ZIP in file.suffixes:
    #     raise FileNotFoundError
    # make the temp directory
    # unzip
    tmpdir.mkdir()
    if ZIP in file.suffixes:
        with zipfile.ZipFile(file, "r") as zref:
            # dump every thing into the tmpdir
            zref.extractall(tmpdir)
    else:
        __gzip(file,tmpdir)

    try:
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

def __gzip(file,tmpdir: StrPath) -> Iterable[Path]:
    if GZIP in file.suffixes:
        with gzip.open(file, "rb") as zref:
            file = tmpdir / file.name.removesuffix(".gz")
            with file.open("wb") as fout:
                shutil.copyfileobj(zref, fout)

def __iterfiles(tmpdir: StrPath) -> Iterable[Path]:
    for file in tmpdir.glob("*"):
        # handle any gziped files
        if GZIP in file.suffixes:
            with gzip.open(file, "rb") as zref:
                file = tmpdir / file.name.removesuffix(".gz")
                with file.open("wb") as fout:
                    shutil.copyfileobj(zref, fout)
        yield file
