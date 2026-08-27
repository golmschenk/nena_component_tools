# TODO: Currently this is prototyping code. Finalize it.
import os
from enum import StrEnum

# TODO: This is duplicating the pipeline variable. But this way is probably better.
class DeploymentType(StrEnum):
    PRODUCTION = 'production'
    DEVELOPMENT = 'development'
    LOCAL = 'local'


def get_deployment_type() -> DeploymentType:
    deployment_type = os.environ.get('NENA_DEPLOYMENT_TYPE', 'local')
    if deployment_type not in DeploymentType:
        raise ValueError(f'Invalid deployment type `{deployment_type}` found in environment variable '
                         f'`NENA_DEPLOYMENT_TYPE`.')
    return DeploymentType(deployment_type)


DEPLOYMENT_TYPE = get_deployment_type()
