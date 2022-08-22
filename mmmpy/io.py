"""
input output
"""

import re
import gzip
import shutil
import zipfile
from pathlib import Path
from contextlib import contextmanager
from typing import Iterable, Union, Hashable

import xarray as xr

from .core import MRMSDataset
from .typing import Engine, StrPath
from .constants import ZIP, GZ, TMPDIR

FILE_PATTERN = re.compile(r"/([A-Za-z]+(?:-|_)?[A-Za-z]+)+")


class CFGribBackend:
    kwargs = {
        "concat_dim": ["heightAboveSea"],
        "backend_kwargs": dict(
            mask_and_scale=True,
            decode_times=True,
            concat_characters=True,
            decode_coords=True,
            # use_cftime="%Y-%m",
            decode_timedelta=None,
            lock=None,
            indexpath="{path}.{short_hash}.idx",
            filter_by_keys={},
            read_keys=[],
            encode_cf=("parameter", "time", "geography", "vertical"),
            squeeze=True,
            time_dims={"valid_time"},
        ),
    }

    def pipe(self, ds: xr.Dataset) -> xr.Dataset:
        duplicates = ["heightAboveSea"]
        # if more than one file was passed the valid_time should be greater than 1
        if ds.valid_time.size > 1:
            # for which we add a new validTime dimension
            ds = ds.expand_dims({"validTime": ds["valid_time"].to_numpy()})
            duplicates.append("validTime")

        return ds.drop("valid_time").drop_duplicates(duplicates)


class NETCDFBackend:
    kwargs = {
        # "data_vars":["unknown"],
        "concat_dim": ["heightAboveSea"],
        "backend_kwargs": dict(
            mask_and_scale=True,
            decode_times=True,
            concat_characters=True,
            decode_coords=True,
            # use_cftime="%Y-%m",
            decode_timedelta=None,
            lock=None,
            indexpath="{path}.{short_hash}.idx",
            filter_by_keys={},
            read_keys=[],
            encode_cf=("parameter", "time", "geography", "vertical"),
            squeeze=True,
            time_dims={"valid_time"},
        ),
    }
    rename = {"valid_time": "validTime"}

    def pipe(self, ds: xr.Dataset) -> xr.Dataset:
        return ds


class ZarrBackend:
    ...


Store = dict[Engine, Union[CFGribBackend, NETCDFBackend, ZarrBackend]]
store: Store = {
    
    "cfgrib": CFGribBackend(),
    "netcdf": NETCDFBackend(),
    "zarr": ZarrBackend(),
}


class VariableError(Exception):
    """
    too many data variables provided
    """


class EngineResolutionError(Exception):
    """
    unable to resolve Engine
    """


def read_mrms(
    files: Iterable[Path] | Path,
    *,
    engine: Engine = None,
    name: Hashable = None,
    latrange: tuple[float, float] = None,
    lonrange: tuple[float, float] = None,
) -> MRMSDataset:
    """
    single function that will attempt to resolve several various mrms filetypes
    """
    if not engine:
        files, engine = __infer_engine(files)

    backend = store.get(engine)

    if not backend:
        raise EngineResolutionError

    elif engine == "cfgrib":
        ds = xr.open_mfdataset(
            files,
            chunks={},
            engine=engine,
            data_vars="minimal",
            combine="nested",
            **backend.kwargs,
        ).pipe(backend.pipe)

    elif engine == "zarr":
        ds = xr.open_zarr(files)

    elif engine == "netcdf4":
        return NotImplemented

    elif engine == "pygrib":
        return NotImplemented

    elif engine == "wgrib2":
        return NotImplemented

    elif engine == "binary":
        return NotImplemented

    elif engine == "legacy":
        return NotImplemented
    else:
        raise NotImplementedError
    # the dataset should only contain a single variable
    if len(ds.data_vars) != 1:
        raise VariableError
    (ds_name,) = ds

    hist = ds.attrs.pop("history", None)
    # if a name was not explicility provided
    if not name:
        # use the known name if unknow infer one from the file name
        name = ds_name if ds_name != "unknown" else __infer_name_from_file(hist)

    return ds.rename({ds_name: name}).pipe(MRMSDataset, name=name)


def __infer_engine(
    files: Iterable[Path] | Path,
) -> tuple[Iterable[Path] | Path, Engine]:
    engine = NotImplemented

    def infer() -> Iterable[Path]:
        for file in files:
            # engine = "cfgrib"...
            yield file

    if isinstance(files, Path):
        # engine = "cfgrib"...
        ...
    else:
        files = infer()

    return files, engine


def __infer_name_from_file(hist: str) -> Hashable:
    """resolve name from `dataset.attr["history"]`"""
    name_list = FILE_PATTERN.findall(hist)
    if name_list:
        return name_list[-1]
    return "UNABLE_TO_RESOLVE_NAME"


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
        __gzip(file, tmpdir)

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


def __gzip(file: Path, tmpdir: StrPath) -> Iterable[Path]:
    if GZ in file.suffixes:
        with gzip.open(file, "rb") as zref:
            file = tmpdir / file.name.removesuffix(GZ)
            with file.open("wb") as fout:
                shutil.copyfileobj(zref, fout)


def __iterfiles(tmpdir: StrPath) -> Iterable[Path]:
    for file in tmpdir.glob("*"):
        # handle any gziped files
        if GZ in file.suffixes:
            with gzip.open(file, "rb") as zref:
                file = tmpdir / file.name.removesuffix(GZ)
                with file.open("wb") as fout:
                    shutil.copyfileobj(zref, fout)
        yield file


# def __iterlevels(baseurl: str) -> Iterator[str]:
#     (html,) = pd.read_html(baseurl)
#     levels = html["Name"].dropna()
#     yield from baseurl + levels[levels.str.contains("MergedReflectivityQC")]


# def __itertimes(url: str, input_dt: datetime, max_seconds: int) -> Iterator[str]:
#     (html,) = pd.read_html(url, skiprows=[1, 2, 3], parse_dates=True)
#     files = html["Name"].dropna()
#     time_delta: pd.Series[datetime] = abs(
#         input_dt - files.str.extract(r"(\d{8}-\d{6})").astype("datetime64[s]").squeeze()
#     )
#     yield from files[time_delta.dt.total_seconds() <= max_seconds]


# def __make_archive(
#     source: Path,
#     destination: Path,
#     archive_type: Archive = "gztar",
# ) -> None:
#     base_name = destination.parent / destination.stem

#     shutil.make_archive(
#         str(base_name), archive_type, root_dir=source.parent, base_dir=source.name
#     )


# def download_files(
#     destination: Path,
#     *,
#     input_dt: datetime = datetime.utcnow(),
#     max_seconds: int = 300,
#     archive: Archive = None,
# ) -> None:
#     """
#     downloads files the the mrms dataset
#     TODO: [SPECIFC PRODUCT SELECTION]
#     -

#     TODO: [MULTI-THREADING]
#     - add an option for multi-threading to alow for simultaneous downloads

#     """
#     baseurl = "http://mrms.ncep.noaa.gov/data/3DRefl/"
#     if not destination.exists():
#         destination.mkdir()
#     with Session() as session:
#         # iterating the first page provides the levels that are avaliable in the 3DRefl database
#         for url in __iterlevels(baseurl):
#             # all of the levels pages are read to get the validtimes to each of the files and file url
#             # then some logic to select only recent files
#             for file in __itertimes(url, input_dt, max_seconds):
#                 try:
#                     # a request is made to hit the file url
#                     r = session.get(url + file, stream=True, headers={"accept": "gzip"})
#                     r.raise_for_status()
#                 except HTTPError:
#                     continue
#                 # the response object is decompressed
#                 with gzip.GzipFile(fileobj=r.raw, mode="rb") as fsrc:
#                     # written to the local drive
#                     with (destination / file.removesuffix(".gz")).open("wb") as fdst:
#                         shutil.copyfileobj(fsrc, fdst)
#     if archive:
#         # passing an archive argument will archive the files
#         # this is useful for the git purposes
#         __make_archive(destination, destination.with_suffix(f".{archive}"))
