import argparse
from pathlib import Path

import pandas as pd

from ._extract import extract
from ._transfer import transfer
from ._load import load
VERBOSE = True

parser = argparse.ArgumentParser()

parser.add_argument("--date", type=str, required=True)
parser.add_argument("--outdir", type=str, required=True)

if __name__ == "__main__":
    args = parser.parse_args()
    outdir = Path("/tmp/data")
    # [EXTRACT]: async download data from the nssl mrms data archive
    paths = pd.Series(extract())
    validtimes = pd.to_datetime(
        paths.apply(lambda p: p.name).str.extract(r"(\d{8}-\d{6})", expand=False)
    )
    if VERBOSE:
        print(f"{len(paths)} files downloaded")
        print(f"collected data for {len(validtimes.unique())} diffrent valid times")

    for _, files in paths.groupby(validtimes):
        # [TRABSFER]: convet grib2 data to normalized xrarry.dataset
        ds = transfer(files)
        # [LOAD]: save the xarray.dataset to a
        load(ds, outdir)
