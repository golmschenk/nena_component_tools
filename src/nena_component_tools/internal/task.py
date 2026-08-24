import abc
import datetime
import itertools
import json
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path

import boto3

from nena_component_tools.internal.environment_constants import DeploymentType, DEPLOYMENT_TYPE

if DEPLOYMENT_TYPE != DeploymentType.LOCAL:
    sqs = boto3.client('sqs')
    events = boto3.client('events')
else:
    sqs = None  # TODO: This shouldn't just be `None` in this case, as it breaks typehinting.
    events = None

type JsonType = dict[str, 'JsonType'] | list['JsonType'] | str | int | float | bool | None
type JsonDictionary = dict[str, JsonType]

logger = logging.getLogger(__name__)


@dataclass
class EventPipelineTaskMetadata:
    input_message_queue_url: str
    input_message_receipt_handle: str
    input_message_id: str
    output_event_correlation_id: str
    output_event_causation_id: str

@dataclass
class LocalTaskMetadata:
    input_event_path: Path

@dataclass
class Task(abc.ABC):
    input_dictionary: JsonDictionary
    _metadata: EventPipelineTaskMetadata | LocalTaskMetadata

    @abc.abstractmethod
    def emit_event(self, event_source: str, output_dictionary: JsonDictionary, mark_task_complete: bool = True) -> None:
        pass

    @abc.abstractmethod
    def log_failure(self, dictionary: JsonDictionary) -> None:
        pass

@dataclass
class EventPipelineTask(Task):
    input_dictionary: JsonDictionary
    _metadata: EventPipelineTaskMetadata

    def emit_event(self, event_source: str, output_dictionary: JsonDictionary, mark_task_complete: bool = True) -> None:
        event_dictionary = {
            'Source': event_source,
            'DetailType': 'task.completed',
            'Detail': json.dumps(
                {
                    'event_correlation_id': self._metadata.output_event_correlation_id,
                    'event_causation_id': self._metadata.output_event_causation_id,
                    'event_id': uuid.uuid4(),
                    'content': output_dictionary,
                }
            ),
        }
        events.put_events(
            Entries=[
                event_dictionary
            ]
        )
        if mark_task_complete:
            sqs.delete_message(QueueUrl=self._metadata.input_message_queue_url, ReceiptHandle=self._metadata.input_message_receipt_handle)

    def log_failure(self, dictionary: JsonDictionary) -> None:
        failure_json_string = json.dumps({
            'input_dictionary': self.input_dictionary,
            'input_message_queue': self._metadata.input_message_queue_url,
            'input_message_id': self._metadata.input_message_id,
            'input_message_receipt_handle': self._metadata.input_message_receipt_handle,
            'task_correlation_id': self._metadata.output_event_correlation_id,
            'task_causation_id': self._metadata.output_event_causation_id,
            'component_report_dictionary': dictionary,
        })
        logger.error(failure_json_string)

@dataclass
class LocalTask(Task):
    input_dictionary: JsonDictionary
    _metadata: LocalTaskMetadata

    def emit_event(self, event_source: str, output_dictionary: JsonDictionary, mark_task_complete: bool = True) -> None:
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
        failure_json_string = json.dumps({
            'input_event_path': self._metadata.input_event_path,
            'input_dictionary': self.input_dictionary,
            'component_report_dictionary': dictionary,
        })
        logger.error(failure_json_string)
