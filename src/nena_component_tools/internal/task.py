# TODO: Currently this is prototyping code. Finalize it.
import json
from dataclasses import dataclass

import boto3

from nena_component_tools.internal.environment_constants import OUTPUT_EVENT_SOURCE

sqs = boto3.client('sqs')
events = boto3.client('events')

type JsonType = dict[str, 'JsonType'] | list['JsonType'] | str | int | float | bool | None
type JsonDictionary = dict[str, JsonType]

@dataclass
class Task:
    input_dictionary: JsonDictionary
    _input_message_queue_url: str
    _input_message_receipt_handle: str
    _input_message_id: str

    def emit_completion_event(self, output_dictionary: JsonDictionary) -> None:
        events.put_events(
            Entries=[
                {
                    'Source': OUTPUT_EVENT_SOURCE,
                    'DetailType': 'task.completed',
                    'Detail': json.dumps(
                        {
                            'triggering_message': {
                                'queue': self._input_message_queue_url,
                                'id': self._input_message_id,
                            },
                            'content': output_dictionary,
                        }
                    ),
                }
            ]
        )
        sqs.delete_message(QueueUrl=self._input_message_queue_url, ReceiptHandle=self._input_message_receipt_handle)

    def log_failure(self, dictionary: JsonDictionary) -> None:
        # TODO: Create this method.
        pass
