"""module of utility decorator functions"""

import uuid
import gzip
import shutil
import zipfile
import warnings
from pathlib import Path
from typing import Callable, TypeVar


StrPath = TypeVar("StrPath", str, Path)

ZIP = ".zip"
GZIP = ".gz"
GRIB = "grib"
GRIB2 = "grib2"
NETCDF = "netcdf"
BINARY = "binary"
TMPDIR = f"/tmp/mmmpy-{uuid.uuid1()}/"


def unzip(tmpdir: StrPath):
    """
    decorator function used to unzip various types of mrms archive data.

    - converts string like paths to Path objects
    - unzips .zip & .gzip
    - yields Path objects to the location the files were unziped too
    - yields the type of file passed netcdf, grib, binary...

    ```
    @mmmpy.unzip("mytmp/folder/")
    def myfunction(files:Path,filetype:str):
        ...
    myfunction("path/to/some.zip")
    ```
    """
    if isinstance(tmpdir, str):
        tmpdir = Path(tmpdir)

    def iterfiles():
        for file in tmpdir.glob("*"):
            # handle any gziped files
            if GZIP in file.suffixes:
                with gzip.open(file) as ref:
                    file = tmpdir / file.name.removesuffix(".gz")
                    with file.open("wb") as fout:
                        shutil.copyfileobj(ref, fout)
            yield file
        # shutil.rmtree(tmpdir)

    # callback functions intended to handle extracting various
    def __outter(func: Callable):
        # @wraps(func)
        def __inner(file: Path | str, *args, **kwargs):
            if tmpdir.exists():
                # clear the tmp directory
                shutil.rmtree(tmpdir)
                # and create an empty one
                tmpdir.mkdir()
            # create Path object from string if string was passed
            if isinstance(file, str):
                file = Path(file)

            assert isinstance(file, Path)
            # validate the path
            if not file.exists():
                raise FileNotFoundError
            # determine if grib2 or netcdf or something else
            elif GRIB in file.name or GRIB2 in file.name:
                filetype = GRIB
            elif NETCDF in file.name:
                filetype = NETCDF
            else:
                filetype = BINARY
                warnings.warn(
                    f"unknown filetype; decoding with binary method {file.name}"
                )
            # handle any passed zipfiles
            if ZIP in file.name:
                with zipfile.ZipFile(file, "r") as ref:
                    # dumpy every thing into the tmpdir
                    ref.extractall(tmpdir)

            return func(iterfiles(), filetype, **kwargs)

        return __inner

    return __outter
