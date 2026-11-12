from astropy.units import UnitBase
import numpy.typing as npt


class VOTableColumnBase:
    """Common data attributes for ordinary columns and time columns."""

    def __init__(self, name: str, ucd: str, unit: UnitBase, array: npt.NDArray, dtype: npt.DTypeLike):
        self.name: str = name
        self.ucd: str = ucd
        self.unit: UnitBase = unit
        self.array: npt.NDArray = array
        self.dtype: npt.DTypeLike = dtype
