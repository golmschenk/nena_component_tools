# TODO: Currently this is prototyping code. Finalize it.
import json
from typing import Iterator

import boto3

from nena_component_tools.internal.environment_constants import QUEUE_URL
from nena_component_tools.internal.task import Task

sqs = boto3.client('sqs')
events = boto3.client('events')


def get_task_iterator() -> Iterator:
    while True:
        resp = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=300,
        )

        messages = resp.get('Messages', [])
        if not messages:
            continue

        msg = messages[0]
        input_message_receipt_handle = msg['ReceiptHandle']
        input_message_id = msg['MessageId']

        try:
            detail = json.loads(msg['Body'])
            message_content = detail.get('content', detail)
            task = Task(
                message_content,
                _input_message_id=input_message_id,
                _input_message_queue_url=QUEUE_URL,
                _input_message_receipt_handle=input_message_receipt_handle,
            )
            yield task
        except Exception:
            pass  # TODO: Log exception.
