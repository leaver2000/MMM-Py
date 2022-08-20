import numpy.typing as npt
from pathlib import Path
from typing import Literal, Mapping, NewType

dict_keys = type({}.keys())

class Dimensions: ...

class Variable:
    def __init__(
        self,
        group,
        name,
        datatype,
        dimensions=(),
        compression=None,
        zlib=False,
        complevel=4,
        shuffle=True,
        szip_coding="nn",
        szip_pixels_per_block=8,
        blosc_shuffle=1,
        fletcher32=False,
        contiguous=False,
        chunksizes=None,
        endian="native",
        least_significant_digit=None,
        fill_value=None,
        chunk_cache=None,
    ): ...
    dimensions: tuple
    dtype: npt.DTypeLike
    ndim: int
    shape: tuple[int, ...]
    scale: ...

class Groups: ...

class Dataset:
    LatGridSpacing: float
    LonGridSpacing: float
    """
    A netCDF Dataset is a collection of dimensions, groups, variables and attributes. Together they describe the meaning of data and relations among data fields stored in a netCDF file. See Dataset.__init__ for more details.

    A list of attribute names corresponding to global netCDF attributes defined for the Dataset can be obtained with the Dataset.ncattrs method. These attributes can be created by assigning to an attribute of the Dataset instance. A dictionary containing all the netCDF attribute name/value pairs is provided by the __dict__ attribute of a Dataset instance.

    The following class variables are read-only and should not be modified by the user.

    dimensions: The dimensions dictionary maps the names of dimensions defined for the Group or Dataset to instances of the Dimension class.

    variables: The variables dictionary maps the names of variables defined for this Dataset or Group to instances of the Variable class.

    groups: The groups dictionary maps the names of groups created for this Dataset or Group to instances of the Group class (the Dataset class is simply a special case of the Group class which describes the root group in the netCDF4 file).

    cmptypes: The cmptypes dictionary maps the names of compound types defined for the Group or Dataset to instances of the CompoundType class.

    vltypes: The vltypes dictionary maps the names of variable-length types defined for the Group or Dataset to instances of the VLType class.

    enumtypes: The enumtypes dictionary maps the names of Enum types defined for the Group or Dataset to instances of the EnumType class.

    data_model: data_model describes the netCDF data model version, one of NETCDF3_CLASSIC, NETCDF4, NETCDF4_CLASSIC, NETCDF3_64BIT_OFFSET or NETCDF3_64BIT_DATA.

    file_format: same as data_model, retained for backwards compatibility.

    disk_format: disk_format describes the underlying file format, one of NETCDF3, HDF5, HDF4, PNETCDF, DAP2, DAP4 or UNDEFINED. Only available if using netcdf C library version >= 4.3.1, otherwise will always return UNDEFINED.

    parent: parent is a reference to the parent Group instance. None for the root group or Dataset instance.

    path: path shows the location of the Group in the Dataset in a unix directory format (the names of groups in the hierarchy separated by backslashes). A Dataset instance is the root group, so the path is simply '/'.

    keepweakref: If True, child Dimension and Variables objects only keep weak references to the parent Dataset or Group.
    """

    dimensions: Dimensions
    variables: dict[str, Variable]
    groups: Groups
    cmptypes: ...
    vltypes: ...
    enumtypes: ...
    data_model: ...
    file_format: ...
    disk_format: ...
    parent: ...
    path: ...
    keepweakref: ...
    def __init__(
        self,
        filename: Path | str,
        mode: Literal["r", "w"] = "r",
        clobber: bool = True,
        diskless: bool = False,
        persist: bool = False,
        keepweakref: bool = False,
        memory: ... = None,
        encoding: ... = None,
        parallel: bool = False,
        comm: ... = None,
        info: ... = None,
        format: str = "NETCDF4",
    ):
        """
        Dataset constructor.

        filename: Name of netCDF file to hold dataset. Can also be a python 3 pathlib instance or the URL of an OpenDAP dataset. When memory is set this is just used to set the filepath().

        mode: access mode. r means read-only; no data can be modified. w means write; a new file is created, an existing file with the same name is deleted. x means write, but fail if an existing file with the same name already exists. a and r+ mean append; an existing file is opened for reading and writing, if file does not exist already, one is created. Appending s to modes r, w, r+ or a will enable unbuffered shared access to NETCDF3_CLASSIC, NETCDF3_64BIT_OFFSET or NETCDF3_64BIT_DATA formatted files. Unbuffered access may be useful even if you don't need shared access, since it may be faster for programs that don't access data sequentially. This option is ignored for NETCDF4 and NETCDF4_CLASSIC formatted files.

        clobber: if True (default), opening a file with mode='w' will clobber an existing file with the same name. if False, an exception will be raised if a file with the same name already exists. mode=x is identical to mode=w with clobber=False.

        format: underlying file format (one of 'NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC', 'NETCDF3_64BIT_OFFSET' or 'NETCDF3_64BIT_DATA'. Only relevant if mode = 'w' (if mode = 'r','a' or 'r+' the file format is automatically detected). Default 'NETCDF4', which means the data is stored in an HDF5 file, using netCDF 4 API features. Setting format='NETCDF4_CLASSIC' will create an HDF5 file, using only netCDF 3 compatible API features. netCDF 3 clients must be recompiled and linked against the netCDF 4 library to read files in NETCDF4_CLASSIC format. 'NETCDF3_CLASSIC' is the classic netCDF 3 file format that does not handle 2+ Gb files. 'NETCDF3_64BIT_OFFSET' is the 64-bit offset version of the netCDF 3 file format, which fully supports 2+ GB files, but is only compatible with clients linked against netCDF version 3.6.0 or later. 'NETCDF3_64BIT_DATA' is the 64-bit data version of the netCDF 3 file format, which supports 64-bit dimension sizes plus unsigned and 64 bit integer data types, but is only compatible with clients linked against netCDF version 4.4.0 or later.

        diskless: If True, create diskless (in-core) file. This is a feature added to the C library after the netcdf-4.2 release. If you need to access the memory buffer directly, use the in-memory feature instead (see memory kwarg).

        persist: if diskless=True, persist file to disk when closed (default False).

        keepweakref: if True, child Dimension and Variable instances will keep weak references to the parent Dataset or Group object. Default is False, which means strong references will be kept. Having Dimension and Variable instances keep a strong reference to the parent Dataset instance, which in turn keeps a reference to child Dimension and Variable instances, creates circular references. Circular references complicate garbage collection, which may mean increased memory usage for programs that create may Dataset instances with lots of Variables. It also will result in the Dataset object never being deleted, which means it may keep open files alive as well. Setting keepweakref=True allows Dataset instances to be garbage collected as soon as they go out of scope, potentially reducing memory usage and open file handles. However, in many cases this is not desirable, since the associated Variable instances may still be needed, but are rendered unusable when the parent Dataset instance is garbage collected.

        memory: if not None, create or open an in-memory Dataset. If mode = r, the memory kwarg must contain a memory buffer object (an object that supports the python buffer interface). The Dataset will then be created with contents taken from this block of memory. If mode = w, the memory kwarg should contain the anticipated size of the Dataset in bytes (used only for NETCDF3 files). A memory buffer containing a copy of the Dataset is returned by the Dataset.close method. Requires netcdf-c version 4.4.1 for mode=r netcdf-c 4.6.2 for mode=w. To persist the file to disk, the raw bytes from the returned buffer can be written into a binary file. The Dataset can also be re-opened using this memory buffer.

        encoding: encoding used to encode filename string into bytes. Default is None (sys.getdefaultfileencoding() is used).

        parallel: open for parallel access using MPI (requires mpi4py and parallel-enabled netcdf-c and hdf5 libraries). Default is False. If True, comm and info kwargs may also be specified.

        comm: MPI_Comm object for parallel access. Default None, which means MPI_COMM_WORLD will be used. Ignored if parallel=False.

        info: MPI_Info object for parallel access. Default None, which means MPI_INFO_NULL will be used. Ignored if parallel=False.
        """
    def filepath(self): ...
    def close(self): ...
    def isopen(self) -> bool: ...
    def sync(self): ...
    def get_variables_by_attribute(self, **kwargs): ...
