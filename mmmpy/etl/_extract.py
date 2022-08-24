"""
Extract
"""
__all__ = ["PandasSession", "ncep_url_generator", "extract"]
import uuid
import gzip
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Iterable, Callable, Iterator, Literal


import numpy as np
import pandas as pd
from requests import Session
from typing import Iterable, Callable, Iterator
from datetime import datetime, timedelta
from numpy.typing import NDArray
import aiofiles
from aiohttp.client import ClientSession


MAX_TASKS = 5
UTC = "UTC"
ACCEPT_HTML = ("accept", "html")

YYMMDD_HHMMSS = r"(\d{8}-\d{6})"

TMP_DIR = Path("/tmp/mmmpy/")


class PandasSession(Session):
    """
    superset of the requests.Session

    added methods:
    - iterseries (function):

    generator function to read the mrms.dataset and yield valid urls based on a condition
    """

    def iterseries(
        self,
        __url: str,
        __callback: Callable[[pd.Series], NDArray[np.bool_]],
    ) -> Iterator[str]:
        r = self.get(__url, verify=False)
        r.raise_for_status()
        (html,) = pd.read_html(r.content)
        directory = html["Name"].dropna()
        yield from __url + directory[__callback(directory)]

def ncep_url_generator(
    parent: Literal["3DRefl"],
    start: datetime,
    max_seconds: int,
) -> Iterable[str]:
    baseurl = f"http://mrms.ncep.noaa.gov/data/{parent}/"
    delta = timedelta(seconds=max_seconds)

    def filter_times(s: pd.Series):
        return (
            s.str.extract(YYMMDD_HHMMSS, expand=False)
            .astype("datetime64[s]")
            .sub(start)
            .abs()
            <= delta
        )

    with PandasSession() as session:
        session.headers.update([ACCEPT_HTML])
        for url in session.iterseries(
            baseurl, lambda s: s.str.contains("MergedReflectivityQC")
        ):
            yield from session.iterseries(url, filter_times)


async def fetch(
    session: ClientSession, url: str, semaphore: asyncio.Semaphore, tmpdir: Path
) -> None:

    async with semaphore:
        print(f"Downloading {url}")
        async with session.get(url, verify=False) as res:
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

def extract(
    group: Literal["3DRefl"] = "3DRefl",
    *,
    start: datetime = ...,
    max_seconds: int = 300,
    tmpdir: Path = ...,
) -> Iterable[Path]:

    urls = ncep_url_generator(group, start, max_seconds)
    if not tmpdir.exists():
        tmpdir.mkdir(parents=True)
    # async download files and gunzip the data
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # TODO: validate this works within a jupyter notebook
        loop.create_task(fetch_concurrent(urls, tmpdir))
    else:
        asyncio.run(fetch_concurrent(urls, tmpdir))
    return tmpdir.glob("*")