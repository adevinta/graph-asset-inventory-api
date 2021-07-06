# pylint: disable=redefined-outer-name

"""Fixtures shared across tests."""

import os

import pytest
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import (
    DriverRemoteConnection,
)

from graph_asset_inventory_api import EnvVarNotSetError
from graph_asset_inventory_api.factory import create_app
from graph_asset_inventory_api.inventory.client import InventoryClient
from graph_asset_inventory_api.inventory import DbTeam
from graph_asset_inventory_api.api import TeamResp


def get_neptune_endpoint():
    """Returns the neptune endpoint got from the environment."""
    neptune_endpoint = os.getenv('NEPTUNE_ENDPOINT', None)
    if neptune_endpoint is None:
        raise EnvVarNotSetError('NEPTUNE_ENDPOINT')
    return neptune_endpoint


@pytest.fixture
def g():
    """Returns the graph traversal source. It takes care of closing the gremlin
    connection after finishing the test."""
    conn = DriverRemoteConnection(get_neptune_endpoint(), 'g')
    g = traversal().withRemote(conn)
    yield g
    conn.close()


@pytest.fixture
def cli():
    """Returns an ``InventoryClient``. It takes care of closing the client
    after finishing the test."""
    cli = InventoryClient(get_neptune_endpoint())
    yield cli
    cli.close()


@pytest.fixture
def flask_cli():
    """Returns a flask test client. It takes care of closing the client after
    finishing the test."""
    conn_app = create_app()
    with conn_app.app.test_client() as flask_cli:
        yield flask_cli


@pytest.fixture
def init_teams(g):
    """Creates an initial set of teams and yields a ``DbTeam`` list. These
    teams are deleted after finishing the test. They can be used to test the
    ``InventoryClient``."""
    init_teams = [
        ('identifier0', 'name0'),
        ('identifier1', 'name1'),
        ('identifier2', 'name2'),
        ('identifier3', 'name3'),
        ('identifier4', 'name4'),
    ]

    # Add teams.
    created_teams = []
    for team in init_teams:
        vteam = g.addV('Team') \
            .property('identifier', team[0]) \
            .property('name', team[1]) \
            .elementMap() \
            .next()
        created_teams.append(DbTeam.from_vteam(vteam))

    yield created_teams

    # Delete teams.
    g.V().drop().iterate()


@pytest.fixture
def init_api_teams(init_teams):
    """Converts the ``DbTeam`` list created by ``init_teams`` into a list of
    dicts that can be used to test the responses of the API endpoints."""
    api_teams = [TeamResp.from_dbteam(t).__dict__ for t in init_teams]
    yield api_teams
