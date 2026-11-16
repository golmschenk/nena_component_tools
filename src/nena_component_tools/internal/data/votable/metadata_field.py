from abc import ABC
from typing import Any


class VOTableMetadataField(ABC):
    def __init__(self, name: str, value: Any):
        self.name: str = name
        self.value: Any = value
