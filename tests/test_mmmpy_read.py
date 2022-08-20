# import shutil
# import zipfile
# from pathlib import Path

# import mmmpy

# # def test_read_binary():
# #     bfile = 'data/MREF3D33L_tile1.20140705.145200.gz'
# #     tile = mmmpy.MosaicTile(bfile)
# #     assert tile.Latitude.max() >= 54 and tile.Latitude.max() <= 55
# #     assert tile.Tile == '1'

# def unzip(filename: Path|str):
#     if isinstance(filename, str):
#         filename = Path(filename)
#     tmpdir = Path("/tmp/mmmpy/")
#     # clear the tmp directory
#     if tmpdir.exists():
#         shutil.rmtree(tmpdir)
#     # create Path object from string
#     if isinstance(filename, str):
#         filename = Path(filename)
#     # validate the file
#     if not filename.exists():
#         raise FileNotFoundError
#     # unzip
#     if ".zip" in filename.suffixes:
#         with zipfile.ZipFile(filename, "r") as zipref:
#             zipref.extractall(tmpdir)
#         file, = tmpdir.glob("*")
#         return
# def test_read_netcdf():
#     unziped = unzip('data/mosaic3d_tile6_20130531-231500.netcdf.zip')
#     # nfile = 'data/mosaic3d_tile6_20130531-231500.netcdf.zip'
#     tile = mmmpy.MosaicTile(unziped)
#     print(tile)
#     # assert tile.Tile == '6'
