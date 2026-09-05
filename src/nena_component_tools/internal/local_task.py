import datetime
import json
import logging

import itertools
from dataclasses import dataclass
from pathlib import Path

from nena_component_tools.internal.task import Task, JsonDictionary

logger = logging.getLogger(__name__)


@dataclass
class LocalTaskMetadata:
    """
    Metadata in a local task.
    """
    input_event_path: Path


@dataclass
class LocalTask(Task):
    """
    Represents a task when running locally.
    """
    input_dictionary: JsonDictionary
    _metadata: LocalTaskMetadata

    def emit_event(self, output_dictionary: JsonDictionary, mark_task_complete: bool = True) -> None:
        """
        Emits an event as a JSON file.

        :param output_dictionary: The content to include in the JSON event file.
        :param mark_task_complete: Whether to mark an event as complete.
        """
        output_events_directory = Path('output_events')
        output_events_directory.mkdir(exist_ok=True, parents=True)
        output_file_stem = f'{datetime.datetime.now():%Y_%m_%d_%H_%M_%S}_from_{self._metadata.input_event_path.stem}'
        for index in itertools.count():
            index_suffix = '' if index == 0 else f'_{index}'
            output_path = output_events_directory.joinpath(f'{output_file_stem}{index_suffix}.json')
            if not output_path.exists():
                break
        # Using `noinspection` below, as the above `count` means `output_path` will always be set.
        # noinspection unbound-local-variable
        with output_path.open('w') as output_file_handle:
            json.dump(output_dictionary, output_file_handle)

    def log_failure(self, dictionary: JsonDictionary) -> None:
        """
        Logs a failure along with the task metadata.

        :param dictionary: The component provided dictionary to include in the log.
        """
        failure_json_string = json.dumps({
            'input_event_path': self._metadata.input_event_path,
            'input_dictionary': self.input_dictionary,
            'component_report_dictionary': dictionary,
        })
        logger.error(failure_json_string)
