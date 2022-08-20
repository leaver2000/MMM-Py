from pathlib import Path
import mmmpy


def test_unzip() -> None:
    @mmmpy.use.unzip()
    def inner(filename) -> bool:
        assert isinstance(filename, Path)
        assert ".zip" not in filename.suffixes
        return True

    assert inner("data/mosaic3d_tile6_20130531-231500.netcdf.zip")
