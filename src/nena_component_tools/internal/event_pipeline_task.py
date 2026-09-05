import json
import logging
import os
import uuid
from dataclasses import dataclass

import boto3

from nena_component_tools.internal.environment_constants import DeploymentType, DEPLOYMENT_TYPE
from nena_component_tools.internal.task import JsonDictionary, Task

logger = logging.getLogger(__name__)

if DEPLOYMENT_TYPE != DeploymentType.LOCAL:
    sqs = boto3.client('sqs')
    events = boto3.client('events')
else:
    sqs = None  # TODO: This shouldn't just be `None` in this case, as it breaks typehinting.
    events = None


@dataclass
class EventPipelineTaskMetadata:
    """
    Metadata for a task in the event-driven pipeline.
    """
    input_message_queue_url: str
    input_message_receipt_handle: str
    input_message_id: str
    output_event_correlation_id: str
    output_event_causation_id: str


@dataclass
class EventPipelineTask(Task):
    """
    A class to represent a task in the event driven pipeline.
    """
    input_dictionary: JsonDictionary
    _metadata: EventPipelineTaskMetadata

    def emit_event(self, output_dictionary: JsonDictionary, mark_task_complete: bool = True) -> None:
        """
        Emits an event in the event-driven pipeline.

        :param output_dictionary: The dictionary to include as the content of the event.
        :param mark_task_complete: Whether to mark the task as completed.
        """
        event_dictionary = {
            'Source': os.environ['NENA_COMPONENT_PIPELINE_NAME'],
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
            sqs.delete_message(QueueUrl=self._metadata.input_message_queue_url,
                               ReceiptHandle=self._metadata.input_message_receipt_handle)

    def log_failure(self, dictionary: JsonDictionary) -> None:
        """
        Log a failure along w with the task metadata.

        :param dictionary: The component provided dictionary to include in the log.
        """
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
