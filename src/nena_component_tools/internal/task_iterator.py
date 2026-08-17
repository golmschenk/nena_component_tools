import json
import logging
import math
from typing import Iterator

import boto3

from nena_component_tools.internal.environment_constants import QUEUE_URL
from nena_component_tools.internal.task import Task

logger = logging.getLogger()


def create_task_iterator(upper_bound_run_time__seconds: int) -> Iterator[Task]:
    """
    Creates a task iterator.

    :param upper_bound_run_time__seconds: The upper bound of runtime of the possible tasks. Will be used to delay a
        message before showing it again to another task worker.
    :return: An infinite iterator over the available tasks in the queue.
    """
    sqs = boto3.client('sqs')
    wait_time__seconds = 60
    message_getting_cost_offset__seconds = 60
    upper_bound_run_time_scale_factor = 2
    if upper_bound_run_time__seconds < message_getting_cost_offset__seconds:
        number_of_messages_to_get = math.ceil(message_getting_cost_offset__seconds / upper_bound_run_time__seconds)
    else:
        number_of_messages_to_get = 1

    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
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
            task = Task(
                message_content,
                _input_message_id=input_message_id,
                _input_message_queue_url=QUEUE_URL,
                _input_message_receipt_handle=input_message_receipt_handle,
                _event_correlation_id=detail.get('event_correlation_id'),
                _event_causation_id=detail.get('event_id'),
            )
            yield task
