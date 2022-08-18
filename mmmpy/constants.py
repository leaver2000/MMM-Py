import numpy as np
from mpl_toolkits.basemap import Basemap, cm

# Hard coding of constants
DEFAULT_CLEVS = np.arange(15) * 5.0
DEFAULT_VAR = "mrefl3d"
DEFAULT_VAR_LABEL = "Reflectivity (dBZ)"
V1_DURATION = 300.0  # seconds
V2_DURATION = 120.0  # seconds
ALTITUDE_SCALE_FACTOR = 1000.0  # Divide meters by this to get something else
DEFAULT_CMAP = cm.GMT_wysiwyg
DEFAULT_PARALLELS = 10  # [20, 37.5, 40, 55]
DEFAULT_MERIDIANS = 10  # [230, 250, 265, 270, 280, 300]
HORIZONTAL_PLOT = [0.1, 0.1, 0.8, 0.8]
VERTICAL_PLOT = [0.1, 0.2, 0.8, 0.8]
THREE_PANEL_SUBPLOT_A = [0.05, 0.10, 0.52, 0.80]
THREE_PANEL_SUBPLOT_B = [0.64, 0.55, 0.33, 0.32]
THREE_PANEL_SUBPLOT_C = [0.64, 0.14, 0.33, 0.32]
DEFAULT_LONLABEL = "Longitude (deg)"
DEFAULT_LATLABEL = "Latitude (deg)"
DEFAULT_ZLABEL = "Height (km MSL)"
DEFAULT_LATRANGE = [20, 55]
DEFAULT_LONRANGE = [-130, -60]
DEFAULT_LINEWIDTH = 0.1

# Following is relevant to MRMS binary format read/write methods
ENDIAN = ""  # Endian currently set automatically by machine type
INTEGER = "i"
DEFAULT_VALUE_SCALE = 10
DEFAULT_DXY_SCALE = 100000
DEFAULT_Z_SCALE = 1
DEFAULT_MAP_SCALE = 1000
DEFAULT_MISSING_VALUE = -99
DEFAULT_MRMS_VARNAME = b"mosaicked_refl1     "  # 20 characters
DEFAULT_MRMS_VARUNIT = b"dbz   "  # 6 characters
DEFAULT_FILENAME = "./mrms_binary_file.dat.gz"

# Following is relevant to MRMS grib2 format read/write
BASE_PATH = "/Users/tjlang/Downloads"
TMPDIR = BASE_PATH + "/tmpdir/"
WGRIB2_PATH = BASE_PATH + "/grib2/wgrib2/"
WGRIB2_NAME = "wgrib2"
MRMS_V3_LATRANGE = [20.0, 55.0]
MRMS_V3_LONRANGE = [-130.0, -60.0]

# v1/v2 changeover occurred on 07/30/2013 around 1600 UTC (epoch = 1375200000)
# See 'https://docs.google.com/document/d/' +
# '1Op3uETOtd28YqZffgvEGoIj0qU6VU966iT_QNUOmqn4/edit'
# for details (doc claims 14 UTC, but CSU has v1 data thru 1550 UTC)
V1_TO_V2_CHANGEOVER_EPOCH_TIME = 1375200000
