import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd

from ._extract import extract
from ._transfer import transfer
from ._load import load

VERBOSE = True

parser = argparse.ArgumentParser()

parser.add_argument("--date", type=str, required=False)
parser.add_argument("--outdir", type=str, required=False)
VDIM = "heightAboveSea"
REF3D = "3DRefl"

if __name__ == "__main__":
    args = parser.parse_args()
    outdir = Path("/tmp/data")
    tmpdir = Path("/tmp/mmmpy")
    # [EXTRACT]: async download data from the nssl mrms data archive
    # yields the paths to the downloaded files in the temp directory
    paths = extract(
        REF3D,
        start=datetime.utcnow(),
        tmpdir=tmpdir,
    )
    # the paths are put into a pandas series
    paths = pd.Series(paths)
    # from which a datetime array is created
    validtimes = pd.to_datetime(
        paths.apply(lambda p: p.name).str.extract(r"(\d{8}-\d{6})", expand=False)
    )
    if VERBOSE:
        print(f"{len(paths)} files downloaded")
        print(f"collected data for {len(validtimes.unique())} diffrent valid times")
    print(paths)
    # then loop over the files, grouping them by the validtimes,
    # this is important for loading the data into the zarr store
    for _, files in paths.groupby(validtimes):
        # [TRANSFER]: convet grib2 data, groupedby validtimes to normalized xrarry.dataset
        ds = transfer(files, vdim=VDIM)
        # [LOAD]: save the xarray.dataset to
        load(ds, store=outdir, vdim=VDIM)
