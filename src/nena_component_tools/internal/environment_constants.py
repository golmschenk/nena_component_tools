import os
from enum import StrEnum


class DeploymentType(StrEnum):
    """
    A enum of the available deployment types.
    """
    PRODUCTION = 'production'
    DEVELOPMENT = 'development'
    LOCAL = 'local'


def get_deployment_type() -> DeploymentType:
    """
    Gets the deployment type of the running deployment.
    """
    deployment_type = os.environ.get('NENA_DEPLOYMENT_TYPE', 'local')
    if deployment_type not in DeploymentType:
        raise ValueError(f'Invalid deployment type `{deployment_type}` found in environment variable '
                         f'`NENA_DEPLOYMENT_TYPE`.')
    return DeploymentType(deployment_type)


DEPLOYMENT_TYPE = get_deployment_type()
