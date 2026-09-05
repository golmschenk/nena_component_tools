import json
import logging
import math
import os
from pathlib import Path
from typing import Iterator

import boto3

from nena_component_tools.internal.environment_constants import DEPLOYMENT_TYPE, DeploymentType
from nena_component_tools.internal.task import Task, EventPipelineTaskMetadata, EventPipelineTask
from nena_component_tools.internal.local_task import LocalTaskMetadata, LocalTask

logger = logging.getLogger()


def create_task_iterator() -> Iterator[Task]:
    """
    Creates a task iterator. When run on a local machine, the iterator iterates over tasks defined by JSON event files
    in a local directory. When run in production, the tasks are defined by polled SQS messages and loops infinitely.

    :return: The task iterator.
    """
    if DEPLOYMENT_TYPE == DeploymentType.LOCAL:
        yield from create_local_task_iterator()
    else:
        yield from create_sqs_task_iterator()


def create_sqs_task_iterator() -> Iterator[Task]:
    """
    Creates a task iterator.

    :return: An infinite iterator over the available tasks in the queue.
    """
    sqs = boto3.client('sqs')
    queue_url = os.environ['NENA_SQS_QUEUE_URL']  # TODO: This should probably be read differently.
    upper_bound_run_time__seconds = int(os.environ['NENA_UPPER_BOUND_RUN_TIME__SECONDS'])
    wait_time__seconds = 60
    message_getting_cost_offset__seconds = 60
    upper_bound_run_time_scale_factor = 2
    if upper_bound_run_time__seconds < message_getting_cost_offset__seconds:
        number_of_messages_to_get = math.ceil(message_getting_cost_offset__seconds / upper_bound_run_time__seconds)
    else:
        number_of_messages_to_get = 1

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=number_of_messages_to_get,
            WaitTimeSeconds=wait_time__seconds,
            VisibilityTimeout=upper_bound_run_time__seconds * upper_bound_run_time_scale_factor,
        )

        messages = response.get('Messages', [])
        for message in messages:
            input_message_receipt_handle = message['ReceiptHandle']
            input_message_id = message['MessageId']
            detail = json.loads(message['Body'])
            message_content = detail.get('content', detail)
            task = EventPipelineTask(
                message_content,
                EventPipelineTaskMetadata(
                    input_message_id=input_message_id,
                    input_message_queue_url=queue_url,
                    input_message_receipt_handle=input_message_receipt_handle,
                    output_event_correlation_id=detail.get('event_correlation_id'),
                    output_event_causation_id=detail.get('event_id'),
                ),
            )
            yield task


def create_local_task_iterator() -> Iterator[Task]:
    """
    Creates a task iterator designed for local component development.

    :return: The task iterator.
    """
    for input_event_index, input_event_json_path in enumerate(Path('input_events').glob('*.json')):
        with input_event_json_path.open() as input_message_json_file_handle:
            input_dictionary = json.load(input_message_json_file_handle)
            task = LocalTask(
                input_dictionary,
                LocalTaskMetadata(
                    input_event_path=input_event_json_path
                ),
            )
            yield task
