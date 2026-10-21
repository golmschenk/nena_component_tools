from dataclasses import dataclass
from pathlib import Path


@dataclass
class LocalTaskMetadata:
    """
    Metadata in a local task.
    """
    input_event_path: Path
