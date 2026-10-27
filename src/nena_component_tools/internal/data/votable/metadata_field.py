from typing import Any

import numpy as np
from astropy.units import Unit
import numpy.typing as npt

from nena_component_tools.internal.data.votable.ucd import verify_ucd


class VOTableMetadataField:
    def __init__(self, name: str, ucd: str, unit: Unit, value: Any, dtype: npt.DTypeLike):
        self.name: str = name
        self.ucd: str = ucd
        self.unit: Unit = unit
        self.value: npt.NDArray = value
        self.dtype: npt.DTypeLike = dtype

    @classmethod
    def new(cls, name: str, ucd: str, unit: Unit, value: npt.NDArray, dtype: npt.DTypeLike | None = None):
        verify_ucd(ucd)
        if dtype is None:
            dtype = np.result_type(value)
        return cls(name=name, ucd=ucd, unit=unit, value=value, dtype=dtype)
