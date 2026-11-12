from astropy.io.votable.tree import TimeSys
from astropy.units import UnitBase
import numpy.typing as npt

from nena_component_tools.internal.data.votable.column import VOTableColumnBase
from nena_component_tools.internal.data.votable.ucd import verify_ucd


class VOTableTimeColumn(VOTableColumnBase):
    def __init__(self, name: str, ucd: str, unit: UnitBase, time_system: TimeSys, array: npt.NDArray, dtype: npt.DTypeLike):
        super().__init__(name=name, ucd=ucd, unit=unit, array=array, dtype=dtype)
        self.time_system: TimeSys = time_system

    @classmethod
    def new(cls, name: str, ucd: str, unit: UnitBase, time_system: TimeSys, array: npt.NDArray,
            dtype: npt.DTypeLike | None = None):
        verify_ucd(ucd)
        if dtype is None:
            dtype = array.dtype
        return cls(name=name, ucd=ucd, unit=unit, time_system=time_system, array=array, dtype=dtype)
