# TODO: Currently this is prototyping code. Finalize it.
import os
from enum import StrEnum

INPUT_BUCKETS = os.environ['INPUT_BUCKETS']
OUTPUT_BUCKETS = os.environ['OUTPUT_BUCKETS']
QUEUE_URL = os.environ['QUEUE_URL']
OUTPUT_EVENT_SOURCE = os.environ.get('OUTPUT_EVENT_SOURCE', 'nena.container')


class DeploymentType(StrEnum):
    PRODUCTION = 'production'
    DEVELOPMENT = 'development'
    LOCAL = 'local'


def get_deployment_type() -> DeploymentType:
    deployment_type = os.environ.get('DEPLOYMENT_TYPE', 'local')
    if deployment_type not in DeploymentType:
        raise ValueError(f'Invalid deployment type `{deployment_type}` found in environment variable '
                         f'`DEPLOYMENT_TYPE`.')
    return DeploymentType(deployment_type)


DEPLOYMENT_TYPE = get_deployment_type()
