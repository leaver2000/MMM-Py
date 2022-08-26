__all__ = ["extract", "transfer", "load"]

import uuid
import gzip
import shutil
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Literal, Iterable 

import requests
import pandas as pd
import numpy as np
# these are enums that I defined that describe the iastate directory
from mmmpy._features import MRMSFeatures, MRMSRegions
from ._extract import extract
from ._transfer import transfer
from ._load import load

GZ =  ".gz"
READ = "r"
WRITE_BINARY = "wb"

class IAStateZip(zipfile.ZipFile):
    def filterinfo(
        self,
        regions: list[MRMSRegions],
        features: list[MRMSFeatures],
    ) -> Iterable[zipfile.ZipInfo]:
        df = pd.DataFrame({"zipInfo": self.infolist(), "path": self.namelist()})
        df = df[df["path"].str.endswith(GZ)]
        df.loc[:, ["validTime", "region", "feature", "name"]] = np.vstack(
            df["path"].str.split("/")
        )
        region_mask = np.any(
            (np.array(regions)[:, np.newaxis] == df["region"].values).T, axis=1
        )
        feature_mask = np.any(
            (np.array(features)[:, np.newaxis] == df["feature"].values).T, axis=1
        )
        yield from df.loc[(region_mask & feature_mask), "zipInfo"]


def iastate_connect(start: datetime, out: Path, fix_zip: bool = True) -> Path:
    url = start.strftime("https://mrms.agron.iastate.edu/%Y/%m/%d/%Y%m%d%H.zip")
    print("downloading mrms data from:", url)
    _, filename = url.rsplit("/", maxsplit=1)
    file = out / filename
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with file.open(WRITE_BINARY) as fd:
            for chunk in r.iter_content(chunk_size=4096):
                fd.write(chunk)
    if fix_zip:
        fix_badzip(file)
    return file


def fix_badzip(corrupt: Path, in_place:bool=True):
    print("attempting to resolve zipfile")

    tmpfile = corrupt.parent / f"{uuid.uuid1()}.zip"

    subprocess.call(
        ["zip", "-FF", corrupt.as_posix(), f"--out={tmpfile.as_posix()}"],
        stdout=subprocess.DEVNULL,
    )
    if in_place:
        corrupt.unlink()
        shutil.move(tmpfile, corrupt)



def main():
    data = Path.cwd().parent / "data"
    zfile = iastate_connect(
        datetime.fromisoformat("2022-06-01T12"), out=data
    )
    assert zfile.is_file()
    # open the zip file
    with IAStateZip(zfile) as zf:
        # filter the info inside of the zip
        for member in zf.filterinfo(regions=["CONUS"], features=["MergedReflectivityQC"]):
            # split the nested product directory
            directory, filename = member.filename.rsplit("/",maxsplit=1)
            # create a new file_path
            file_path = zfile.parent / directory
            if not file_path.exists():
                file_path.mkdir(parents=True)
            file = file_path / filename.removesuffix(GZ)
            # read the member from the zip file
            with zf.open(member,READ) as zref:
                # open a new file
                with file.open(WRITE_BINARY) as fdst:
                    # wrote the unziped & gunziped file to the new folder
                    fdst.write(gzip.decompress(zref.read()))


if __name__ == "__main__":
    main()