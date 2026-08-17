# TODO: Currently this is prototyping code. Finalize it.
import json
import logging
import uuid
from dataclasses import dataclass

import boto3

sqs = boto3.client('sqs')
events = boto3.client('events')

type JsonType = dict[str, 'JsonType'] | list['JsonType'] | str | int | float | bool | None
type JsonDictionary = dict[str, JsonType]

logger = logging.getLogger(__name__)


@dataclass
class Task:
    input_dictionary: JsonDictionary
    _input_message_queue_url: str
    _input_message_receipt_handle: str
    _input_message_id: str
    _event_correlation_id: str
    _event_causation_id: str

    def emit_event(self, event_source: str, output_dictionary: JsonDictionary, mark_task_complete: bool = True) -> None:
        events.put_events(
            Entries=[
                {
                    'Source': event_source,
                    'DetailType': 'task.completed',
                    'Detail': json.dumps(
                        {
                            'event_correlation_id': self._event_correlation_id,
                            'event_causation_id': self._event_causation_id,
                            'event_id': uuid.uuid4(),
                            'content': output_dictionary,
                        }
                    ),
                }
            ]
        )
        if mark_task_complete:
            sqs.delete_message(QueueUrl=self._input_message_queue_url, ReceiptHandle=self._input_message_receipt_handle)

    def log_failure(self, dictionary: JsonDictionary) -> None:
        failure_json_string = json.dumps({
            'input_dictionary': self.input_dictionary,
            'input_message': {
                'queue': self._input_message_queue_url,
                'id': self._input_message_id,
                'receipt_handle': self._input_message_receipt_handle,
            },
            'component_report_dictionary': dictionary,
        })
        logger.error(failure_json_string)
