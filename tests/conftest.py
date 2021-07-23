"""Fixtures shared across tests."""

# pylint: disable=redefined-outer-name

import os
from datetime import datetime

import pytest
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection import (
    DriverRemoteConnection,
)

from graph_asset_inventory_api import EnvVarNotSetError
from graph_asset_inventory_api.factory import create_app
from graph_asset_inventory_api.inventory.client import InventoryClient
from graph_asset_inventory_api.inventory import (
    DbTeam,
    DbAsset,
    DbParentOf,
    DbOwns,
)
from graph_asset_inventory_api.api import (
    TeamResp,
    AssetResp,
)


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


# Teams.


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


# Assets.


@pytest.fixture
def init_assets(g):
    """Creates an initial set of assets and yields a ``DbAsset`` list. These
    assets are deleted after finishing the test. They can be used to test the
    ``InventoryClient``."""
    # (type, identifier, first_seen, last_seen, expiration)
    assets = [
        ('type0', 'identifier0', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),
        ('type0', 'identifier1', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),

        ('type1', 'identifier0', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),
        ('type1', 'identifier1', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),
        ('type1', 'identifier2', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),
        ('type1', 'identifier3', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),

        ('type2', 'identifier0', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),
        ('type2', 'identifier1', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),

        ('type3', 'identifier0', '2021-07-01T01:00:00', '2021-07-07T01:00:00',
            '2021-07-14T01:00:00'),
    ]

    # Add assets.
    created_assets = []
    for asset in assets:
        asset_type = asset[0]
        asset_identifier = asset[1]
        first_seen = datetime.fromisoformat(asset[2])
        last_seen = datetime.fromisoformat(asset[3])
        expiration = datetime.fromisoformat(asset[4])
        vasset = g.addV('Asset') \
            .property('type', asset_type) \
            .property('identifier', asset_identifier) \
            .property('first_seen', first_seen) \
            .property('last_seen', last_seen) \
            .property('expiration', expiration) \
            .elementMap() \
            .next()
        created_assets.append(DbAsset.from_vasset(vasset))

    yield created_assets

    # Delete assets.
    g.V().drop().iterate()


@pytest.fixture
def init_api_assets(init_assets):
    """Converts the ``DbAsset`` list created by ``init_assets`` into a list of
    dicts that can be used to test the responses of the API endpoints."""
    api_assets = [AssetResp.from_dbasset(t).__dict__ for t in init_assets]
    yield api_assets


# Parents.


@pytest.fixture
def init_parents(g, init_assets):
    """Creates an initial set of ``parent_of`` edges and yields a dict of the
    form ``{vid0: [DbParentOf], vid1: [DbParentOf]}``. The edges are deleted
    after finishing the test. They can be used to test the
    ``InventoryClient``."""
    edges = {
        # child_idx: [(parent_idx, first_seen, last_seen, expiration)]
        0: [
            (2, '2021-07-01T01:00:00', '2021-07-07T01:00:00',
                '2021-07-14T01:00:00'),
            (3, '2021-07-01T01:00:00', '2021-07-07T01:00:00',
                '2021-07-14T01:00:00'),
            (4, '2021-07-01T01:00:00', '2021-07-07T01:00:00',
                '2021-07-14T01:00:00'),
            (5, '2021-07-01T01:00:00', '2021-07-07T01:00:00',
                '2021-07-14T01:00:00'),
        ],
        1: [
            (6, '2021-07-01T01:00:00', '2021-07-07T01:00:00',
                '2021-07-14T01:00:00'),
            (7, '2021-07-01T01:00:00', '2021-07-07T01:00:00',
                '2021-07-14T01:00:00'),
            (8, '2021-07-01T01:00:00', '2021-07-07T01:00:00',
                '2021-07-14T01:00:00'),
        ],
        2: [],
    }

    # Add ``parent_of`` edges.
    dbparents = {}
    for child_idx, parents in edges.items():
        child_vid = init_assets[child_idx].vid
        dbparents[child_vid] = []
        for parent in parents:
            parent_vid = init_assets[parent[0]].vid
            first_seen = datetime.fromisoformat(parent[1])
            last_seen = datetime.fromisoformat(parent[2])
            expiration = datetime.fromisoformat(parent[3])

            eparentof = g \
                .V(parent_vid).addE('parent_of').to(__.V(child_vid)) \
                .property('first_seen', first_seen) \
                .property('last_seen', last_seen) \
                .property('expiration', expiration) \
                .elementMap() \
                .next()

            dbparents[child_vid].append(DbParentOf.from_eparentof(eparentof))

    yield dbparents

    # Delete edges.
    g.E().drop().iterate()


# Owners.


@pytest.fixture
def init_owners(g, init_teams, init_assets):
    """Creates an initial set of ``owns`` edges and yields a dict of the form
    ``{vid0: [DbOwns], vid1: [DbOwns]}``. The edges are deleted after finishing
    the test. They can be used to test the ``InventoryClient``."""
    edges = {
        # asset_idx: [(asset_idx, start_time, end_time)]
        0: [
            (1, '2021-07-01T01:00:00', '2021-07-07T01:00:00'),
            (2, '2021-07-01T01:00:00', '2021-07-07T01:00:00'),
            (3, '2021-07-01T01:00:00', '2021-07-07T01:00:00'),
        ],
        1: [
            (4, '2021-07-01T01:00:00', '2021-07-07T01:00:00'),
        ],
        2: [],
    }

    # Add ``owns`` edges.
    dbowners = {}
    for asset_idx, owners in edges.items():
        asset_vid = init_assets[asset_idx].vid
        dbowners[asset_vid] = []
        for owner in owners:
            team_vid = init_teams[owner[0]].vid
            start_time = datetime.fromisoformat(owner[1])
            end_time = datetime.fromisoformat(owner[2])

            eowns = g \
                .V(team_vid).addE('owns').to(__.V(asset_vid)) \
                .property('start_time', start_time) \
                .property('end_time', end_time) \
                .elementMap() \
                .next()

            dbowners[asset_vid].append(DbOwns.from_eowns(eowns))

    yield dbowners

    # Delete edges.
    g.E().drop().iterate()
