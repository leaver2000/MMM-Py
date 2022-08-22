"""
functions to extract and archive mrms data from a few sources
"""
__all__ = ["from_ncep", "from_mtarchive"]
from email.generator import Generator
import re
import gzip
import shutil
from pathlib import Path
from typing import Iterator, Callable
from datetime import datetime, timedelta
from typing import Iterator

import pandas as pd
import numpy as np
from numpy.typing import NDArray
from requests import Session, HTTPError
from .typing import Archive
from .constants import GZ


HEADERS = {"accept": "gzip"}

YYMMDD_HHMMSS = r"(\d{8}-\d{6})"
DT64S = "datetime64[s]"
ACCEPT_HTML = ("accept", "html")
ACCEPT_GZIP = ("accept", "gzip")


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
) -> Generator:
    baseurl = f"http://mrms.ncep.noaa.gov/data/{parent}/"
    delta = timedelta(seconds=max_seconds)

    def filter_times(s: pd.Series):
        return (
            s.str.extract(YYMMDD_HHMMSS, expand=False).astype(DT64S).sub(input_dt).abs()
            <= delta
        )

    with PandasSession() as session:
        session.headers.update([ACCEPT_HTML])
        for url in session.iterseries(
            baseurl, lambda s: s.str.contains("MergedReflectivityQC")
        ):
            yield from session.iterseries(url, filter_times)


def from_ncep(
    destination: Path,
    *,
    input_dt: datetime = datetime.utcnow(),
    max_seconds: int = 300,
    archive: Archive = None,
    headers=HEADERS,
) -> None:
    """
    baseurl = "http://mrms.ncep.noaa.gov/data/3DRefl/"

    downloads files the the mrms dataset
    TODO: [SPECIFC PRODUCT SELECTION]
    -

    TODO: [MULTI-THREADING]
    - add an option for multi-threading to alow for simultaneous downloads

    """
    baseurl = "http://mrms.ncep.noaa.gov/data/3DRefl/"
    if not destination.exists():
        destination.mkdir()
    with Session() as session:
        # iterating the first page provides the levels that are avaliable in the 3DRefl database
        for url in __iterlevels(baseurl):
            # all of the levels pages are read to get the validtimes to each of the files and file url
            # then some logic to select only recent files
            for file in __itertimes(url, input_dt, max_seconds):
                try:
                    # a request is made to hit the file url
                    r = session.get(url + file, stream=True, headers=headers)
                    r.raise_for_status()
                except HTTPError:
                    continue
                # the response object is decompressed
                with gzip.GzipFile(fileobj=r.raw, mode="rb") as fsrc:
                    file = destination / file.removesuffix(GZ)
                    # written to the local drive
                    with file.open("wb") as fdst:
                        shutil.copyfileobj(fsrc, fdst)
    if archive:
        # passing an archive argument will archive the files
        # this is useful for the git purposes
        __make_archive(destination, destination.with_suffix(f".{archive}"))


def from_mtarchive(start: datetime, stop: datetime) -> NotImplemented:
    """
    baseurl = https://mtarchive.geol.iastate.edu/{year}/{month}/{day}/mrms/ncep/
    """
    url_template = "https://mtarchive.geol.iastate.edu/%Y/%m/%d/mrms/ncep/"
    dr = pd.date_range(start=start, stop=stop, freq="D")
    for url in dr.strftime(url_template):
        print(url)
    return NotImplemented


def __iterlevels(baseurl: str) -> Iterator[str]:
    (html,) = pd.read_html(baseurl)
    levels = html["Name"].dropna()
    yield from baseurl + levels[levels.str.contains("MergedReflectivityQC")]


def __itertimes(url: str, input_dt: datetime, max_seconds: int) -> Iterator[str]:
    (html,) = pd.read_html(url, skiprows=[1, 2, 3], parse_dates=True)
    files = html["Name"].dropna()
    time_delta: pd.Series[datetime] = abs(
        input_dt - files.str.extract(r"(\d{8}-\d{6})").astype("datetime64[s]").squeeze()
    )
    yield from files[time_delta.dt.total_seconds() <= max_seconds]


def __make_archive(
    source: Path,
    destination: Path,
    archive_type: Archive = "gztar",
) -> None:
    base_name = destination.parent / destination.stem

    shutil.make_archive(
        str(base_name), archive_type, root_dir=source.parent, base_dir=source.name
    )
