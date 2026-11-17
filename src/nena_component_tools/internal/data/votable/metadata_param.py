from typing import Any

import numpy as np
from astropy.units import UnitBase
import numpy.typing as npt

from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField
from nena_component_tools.internal.data.votable.ucd import verify_ucd


class VOTableMetadataParam(VOTableMetadataField):
    def __init__(self, name: str, ucd: str, unit: UnitBase, value: Any, dtype: npt.DTypeLike):
        super().__init__(name=name, value=value)
        self.ucd: str = ucd
        self.unit: UnitBase = unit
        self.dtype: npt.DTypeLike = dtype

    @classmethod
    def new(cls, name: str, value: Any, ucd: str, unit: UnitBase, dtype: npt.DTypeLike | None = None):
        verify_ucd(ucd, controlled_vocabulary=False)
        if dtype is None:
            dtype = np.result_type(value)
        return cls(name=name, ucd=ucd, unit=unit, value=value, dtype=dtype)
