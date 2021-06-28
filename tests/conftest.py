# pylint: disable=redefined-outer-name

import os

import pytest
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import (
    DriverRemoteConnection,
)

from graph_asset_inventory_api.factory import create_app
from graph_asset_inventory_api.inventory.client import InventoryClient
from graph_asset_inventory_api.inventory.types import DbTeam
from graph_asset_inventory_api.api.types import TeamResp


def get_neptune_endpoint():
    neptune_endpoint = os.getenv('NEPTUNE_ENDPOINT', None)
    if neptune_endpoint is None:
        raise 'missing env var NEPTUNE_ENDPOINT'
    return neptune_endpoint


@pytest.fixture
def g():
    conn = DriverRemoteConnection(get_neptune_endpoint(), 'g')
    g = traversal().withRemote(conn)
    yield g
    conn.close()


@pytest.fixture
def cli():
    cli = InventoryClient(get_neptune_endpoint())
    yield cli
    cli.close()


@pytest.fixture
def flask_cli():
    conn_app = create_app()
    with conn_app.app.test_client() as flask_cli:
        yield flask_cli


@pytest.fixture
def init_teams(g):
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
    api_teams = [TeamResp.from_dbteam(t).__dict__ for t in init_teams]
    yield api_teams
