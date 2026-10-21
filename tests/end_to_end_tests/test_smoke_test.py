from pathlib import Path

from nena_component_tools.internal.local_task import LocalTask
from nena_component_tools.internal.local_task_metadata import LocalTaskMetadata


def test_smoke_test():
    _ = LocalTask(
        {'a': 1},
        LocalTaskMetadata(input_event_path=Path('fake_path.json')),
    )
