from astropy.units import UnitBase
import numpy.typing as npt

from nena_component_tools.internal.data.votable.column_base import VOTableColumnBase
from nena_component_tools.internal.data.votable.ucd import verify_ucd, verify_not_time_system_ucd


class VOTableColumn(VOTableColumnBase):
    @classmethod
    def new(cls, name: str, ucd: str, unit: UnitBase, array: npt.NDArray, dtype: npt.DTypeLike | None = None):
        verify_ucd(ucd)
        verify_not_time_system_ucd(ucd)
        if dtype is None:
            dtype = array.dtype
        return cls(name=name, ucd=ucd, unit=unit, array=array, dtype=dtype)
