"""This module makes easier to connect to a Gremlin server with different
authentication methods."""

from os import getenv
from urllib.parse import urlparse

from gremlin_python.driver.driver_remote_connection import (
    DriverRemoteConnection,
)
from neptune_python_utils.gremlin_utils import GremlinUtils
from neptune_python_utils.endpoints import Endpoints

from graph_asset_inventory_api import EnvVarNotSetError


def get_connection(gremlin_endpoint, auth_mode='none'):
    """Returns a connection to the corresponding gremlin server. If
    ``auth_mode`` is ``neptune_iam``, IAM credentials are used for
    authentication against a Neptune cluster."""
    if auth_mode == 'neptune_iam':
        parse_result = urlparse(gremlin_endpoint)
        neptune_hostname = parse_result.hostname
        neptune_port = parse_result.port
        return get_neptune_iam_connection(neptune_hostname, neptune_port)

    if auth_mode == 'none':
        return DriverRemoteConnection(gremlin_endpoint, 'g')

    raise ValueError('unknown auth mode')


def get_neptune_iam_connection(neptune_hostname, neptune_port=8182):
    """Returns a Neptune connection using IAM authentication. It expects the
    environment variable ``AWS_REGION`` to exist. Typically, it is used in the
    following way:

        from gremlin_python.process.anonymous_traversal import traversal
        from graph_asset_inventory_api import neptune

        conn = neptune.connect_with_iam(neptune_hostname)
        g = traversal().withRemote(conn)
        g.V().limit(10).valueMap().toList()
    """
    aws_region = getenv('AWS_REGION', None)
    if aws_region is None:
        raise EnvVarNotSetError('AWS_REGION')

    endpoints = Endpoints(
        neptune_endpoint=neptune_hostname,
        neptune_port=neptune_port,
        region_name=aws_region,
    )
    gremlin_utils = GremlinUtils(endpoints)

    return gremlin_utils.remote_connection()
