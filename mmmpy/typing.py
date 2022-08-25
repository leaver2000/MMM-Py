__all__ = ["StrPath", "Engine", "Archive"]
from pathlib import Path
from typing import TypeVar, Literal

StrPath = TypeVar("StrPath", str, Path)
Engine = Literal["netcdf4", "cfgrib", "binary"]
Archive = Literal["zip", "tar", "gztar", "bztar", "xztar"]

