"""
functions to extract and archive mrms data from a few sources
"""
__all__ = ["from_ncep", "from_mtarchive"]
import uuid
import gzip
import asyncio
import shutil
from pathlib import Path
from typing import Iterable, Callable, Iterator
from datetime import datetime, timedelta


import aiofiles
from aiohttp.client import ClientSession


import zarr
import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray
from requests import Session


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
    tmpfile = tmpdir / f"{uuid.uuid1()}.{GRIB2}"
    async with sem:
        print(f"Downloading {url}")
        async with session.get(url) as res:
            content = await res.read()

        async with aiofiles.open(tmpfile, "+wb") as tmp:
            await tmp.write(gzip.decompress(content))


async def fetch_concurrent(
    urls: Iterable[str],
    tmpdir: Path,
) -> None:
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


def open_dataset(file: Path, store: Path) -> None:

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

    path = f"{np.datetime_as_string(vt,timezone=UTC)}/{height}"

    ds.expand_dims({"validTime": [vt], "heightAboveSea": [height]}).drop(
        "valid_time"
    ).to_zarr(store=zarr.DirectoryStore(store / path), mode="a")


def main(store: Path):
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
    for file in tmpdir.glob(f"*.{GRIB2}"):
        open_dataset(file, store)
    # removed the data directory
    if tmpdir.exists():
        shutil.rmtree(tmpdir)
