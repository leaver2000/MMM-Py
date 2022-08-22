"""
functions to extract and archive mrms data from a few sources
"""
__all__ = ["from_ncep", "from_mtarchive", "main"]
import re
import uuid
import gzip
import asyncio
import shutil
from pathlib import Path
from typing import Iterable, Callable, Iterator
from datetime import datetime, timedelta

import aiofiles
from aiohttp.client import ClientSession


import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray
from requests import Session


UTC = "UTC"
MAX_TASKS = 5
CFGRIB = "cfgrib"
GRIB2 = "grib2"
ACCEPT_HTML = ("accept", "html")
ACCEPT_GZIP = ("accept", "gzip")

TMP_DIR = Path("/tmp/mmmpy/")

FILE_NAME_PATTERN = re.compile(r"/([A-Za-z]+(?:-|_)?[A-Za-z]+)+")
YYMMDD_HHMMSS = r"(\d{8}-\d{6})"

datetime64m = "datetime64[m]"
datetime64s = "datetime64[s]"

class PandasSession(Session):
    def iterseries(
        self,
        __url: str,
        __callback: Callable[[pd.Series], NDArray[np.bool_]],
    ) -> Iterator[str]:
        r = self.get(__url)
        r.raise_for_status()
        (html,) = pd.read_html(r.content)
        directory = html["Name"].dropna()
        yield from __url + directory[__callback(directory)]


def ncep_url_generator(
    parent="3DRefl",
    input_dt: datetime = datetime.utcnow(),
    max_seconds: int = 300,
) -> Iterable[str]:
    baseurl = f"http://mrms.ncep.noaa.gov/data/{parent}/"
    delta = timedelta(seconds=max_seconds)

    def filter_times(s: pd.Series):
        return (
            s.str.extract(YYMMDD_HHMMSS, expand=False)
            .astype(datetime64s)
            .sub(input_dt)
            .abs()
            <= delta
        )

    with PandasSession() as session:
        session.headers.update([ACCEPT_HTML])
        for url in session.iterseries(
            baseurl, lambda s: s.str.contains("MergedReflectivityQC")
        ):
            yield from session.iterseries(url, filter_times)


async def fetch(session: ClientSession, url: str, sem: asyncio.Semaphore, tmpdir: Path):

    async with sem:
        print(f"Downloading {url}")
        async with session.get(url) as res:
            content = await res.read()

        async with aiofiles.open(
            tmpdir / url.split("/")[-1].removesuffix(".gz"), "+wb"
        ) as tmp:
            await tmp.write(gzip.decompress(content))


async def fetch_concurrent(
    urls: Iterable[str],
    tmpdir: Path,
) -> None:
    """
    async downloadinging of data from the ncewp data server
    """
    # In computer science, a semaphore is a
    # variable or abstract data type used to
    # control access to a common resource by
    # multiple threads and avoid critical
    # section problems in a concurrent system
    # such as a multitasking operating system.
    # Semaphores are a type of synchronization primitive.
    sem = asyncio.Semaphore(MAX_TASKS)
    async with ClientSession(auto_decompress=False) as session:
        await asyncio.gather(*(fetch(session, url, sem, tmpdir) for url in urls))


def dims(ds: xr.Dataset) -> xr.Dataset:
    duplicates = ["heightAboveSea"]
    # if more than one file was passed the valid_time should be greater than 1
    if ds.valid_time.size > 1:
        # for which we add a new validTime dimension
        ds = ds.expand_dims({"validTime": ds["valid_time"].to_numpy()})
        duplicates.append("validTime")

    return ds.drop("valid_time").drop_duplicates(duplicates)




def open_dataset(files: Iterable[Path]) -> xr.Dataset:

    ds = xr.open_mfdataset(
        files,
        chunks={},
        engine="cfgrib",
        data_vars="minimal",
        combine="nested",
        concat_dim=["heightAboveSea"],
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
    ds = (
        ds.expand_dims(
            {
                "validTime": [ds["valid_time"].to_numpy()],
            }
        )
        .drop("valid_time")
        .drop_duplicates(["validTime", "heightAboveSea"])
    )

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

def main(store: Path):
    # [EXTRACT]
    # crawl the dataset listing
    urls = ncep_url_generator(
        parent="3DRefl", input_dt=datetime.utcnow(), max_seconds=300
    )
    # create a unique temp directory
    tmpdir = TMP_DIR / str(uuid.uuid1())
    if not tmpdir.exists():
        tmpdir.mkdir(parents=True)
    # async download files and gunzip the data
    asyncio.run(fetch_concurrent(urls, tmpdir))
    # convert the dataformat from grib -> zarr
    paths = pd.Series(tmpdir.glob(f"*.{GRIB2}"))
    validtimes = pd.to_datetime(
        paths.apply(lambda p: p.name).str.extract(r"(\d{8}-\d{6})", expand=False)
    )
    # group all of the downloaded files by the validtimes.
    for _, files in paths.groupby(validtimes):
        # ##########################
        #       [TRANSFER]
        # ##########################
        ds = open_dataset(tuple(files))
        dsname, = ds
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
        
    # removed the data directory
    if tmpdir.exists():
        shutil.rmtree(tmpdir)
