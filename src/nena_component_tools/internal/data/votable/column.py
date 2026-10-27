from astropy.units import Unit
import numpy.typing as npt

from nena_component_tools.internal.data.votable.ucd import verify_ucd, verify_not_time_system_ucd


class VOTableColumn:
    def __init__(self, name: str, ucd: str, unit: Unit, array: npt.NDArray, dtype: npt.DTypeLike):
        self.name: str = name
        self.ucd: str = ucd
        self.unit: Unit = unit
        self.array: npt.NDArray = array
        self.dtype: npt.DTypeLike = dtype

    @classmethod
    def new(cls, name: str, ucd: str, unit: Unit, array: npt.NDArray, dtype: npt.DTypeLike | None = None):
        verify_ucd(ucd)
        verify_not_time_system_ucd(ucd)
        if dtype is None:
            dtype = array.dtype
        return cls(name=name, ucd=ucd, unit=unit, array=array, dtype=dtype)
