"""Fixtures shared across tests."""

# pylint: disable=redefined-outer-name

import os
import uuid
from datetime import datetime

import pytest
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import (
    T,
    Cardinality,
)

from graph_asset_inventory_api import EnvVarNotSetError
from graph_asset_inventory_api.factory import create_app
from graph_asset_inventory_api.inventory.client import InventoryClient

from graph_asset_inventory_api.inventory.universe import (
    Universe,
    UniverseVersion,
)
from graph_asset_inventory_api.inventory import (
    DbTeam,
    DbAsset,
    DbParentOf,
    DbOwns,
    CURRENT_UNIVERSE,
)
from graph_asset_inventory_api.api import (
    TeamResp,
    AssetResp,
    ParentOfResp,
    OwnsResp,
)
from graph_asset_inventory_api import gremlin


def get_gremlin_endpoint():
    """Returns the gremlin endpoint from the environment."""
    gremlin_endpoint = os.getenv('GREMLIN_ENDPOINT', None)
    if gremlin_endpoint is None:
        raise EnvVarNotSetError('GREMLIN_ENDPOINT')
    return gremlin_endpoint


def get_auth_mode():
    """Returns the auth mode from the environment."""
    return os.getenv('GREMLIN_AUTH_MODE', 'none')


@pytest.fixture
def g():
    """Returns the graph traversal source. It takes care of closing the gremlin
    connection after finishing the test. All vertices are deleted on both
    the setup and teardown stage of this fixture."""
    conn = gremlin.get_connection(get_gremlin_endpoint(), get_auth_mode())
    g = traversal().withRemote(conn)

    g.V().drop().iterate()

    yield g

    g.V().drop().iterate()

    conn.close()


@pytest.fixture
def universe(g):
    """Creates the current universe vertex"""
    create_universe(g, CURRENT_UNIVERSE)


@pytest.fixture
def cli(g, universe):  # pylint: disable=unused-argument
    """Returns an ``InventoryClient``. It takes care of closing the client
    after finishing the test."""
    cli = InventoryClient(get_gremlin_endpoint(), get_auth_mode())

    yield cli

    cli.close()


@pytest.fixture
def flask_cli(g):  # pylint: disable=unused-argument
    """Returns a flask test client. It takes care of closing the client after
    finishing the test."""
    conn_app = create_app()

    with conn_app.app.test_client() as flask_cli:
        yield flask_cli


@pytest.fixture
def unknown_uuid():
    """Returns a random UUID."""
    return str(uuid.uuid4())


# Teams.


@pytest.fixture
def init_teams(g):
    """Creates an initial set of teams and yields a ``DbTeam`` list. They can
    be used to test the ``InventoryClient``."""

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
            .property(T.id, str(uuid.uuid4())) \
            .property(Cardinality.single, 'identifier', team[0]) \
            .property(Cardinality.single, 'name', team[1]) \
            .sideEffect(
                __.addE("universe_of")
                .from_(
                    __.V()
                    .hasLabel('Universe')
                    .has('namespace', CURRENT_UNIVERSE.namespace)
                    .has('version', CURRENT_UNIVERSE.version.int_version)
                )
            ) \
            .elementMap() \
            .next()
        created_teams.append(DbTeam.from_vteam(vteam))

    created_teams.sort(key=lambda x: x.vid)

    yield created_teams


@pytest.fixture
def new_universe():
    """Creates a universe with a newer version so it can be used in tests as a
    universe newer than the current one.``."""
    yield Universe(
        UniverseVersion.from_int_version(
          CURRENT_UNIVERSE.version.int_version + 1
        )
    )


@pytest.fixture
def init_new_universe_teams(g, new_universe):
    """Creates an initial set of teams and yields a ``DbTeam`` list. They can
    be used to test the ``InventoryClient``."""
    init_teams = [
        ('identifier0', 'name0'),
        ('identifier1', 'name1'),
        ('identifier2', 'name2'),
        ('identifier3', 'name3'),
    ]
    create_universe(g, new_universe)
    # Add teams.
    created_teams = []
    for team in init_teams:
        vteam = g.addV('Team') \
            .property(T.id, str(uuid.uuid4())) \
            .property(Cardinality.single, 'identifier', team[0]) \
            .property(Cardinality.single, 'name', team[1]) \
            .sideEffect(
                __.addE("universe_of")
                .from_(
                    __.V()
                    .hasLabel('Universe')
                    .has('namespace', new_universe.namespace)
                    .has('version', new_universe.version.int_version)
                )
            ) \
            .elementMap() \
            .next()
        created_teams.append(DbTeam.from_vteam(vteam))

    created_teams.sort(key=lambda x: x.vid)

    yield created_teams


@pytest.fixture
def team_not_in_current_universe(init_teams):
    """Returns a team that does not exists in the current universe."""
    return init_teams[4]


@pytest.fixture
def init_api_teams(init_teams):
    """Converts the ``DbTeam`` list created by ``init_teams`` into a list of
    dicts that can be used to test the responses of the API endpoints."""
    api_teams = [TeamResp.from_dbteam(t).__dict__ for t in init_teams]
    yield api_teams


# Assets.


@pytest.fixture
def init_assets(g):
    """Creates an initial set of assets and yields a ``DbAsset`` list.  They
    can be used to test the ``InventoryClient``."""
    # (type, identifier, first_seen, last_seen, expiration)
    assets = [
        (
            'type0', 'identifier0',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),
        (
            'type0', 'identifier1',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),

        (
            'type1', 'identifier0',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),
        (
            'type1', 'identifier1',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),
        (
            'type1', 'identifier2',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),
        (
            'type1', 'identifier3',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),

        (
            'type2', 'identifier0',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),
        (
            'type2', 'identifier1',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),

        (
            'type3', 'identifier0',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),
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
            .property(T.id, str(uuid.uuid4())) \
            .property(Cardinality.single, 'type', asset_type) \
            .property(Cardinality.single, 'identifier', asset_identifier) \
            .property(Cardinality.single, 'first_seen', first_seen) \
            .property(Cardinality.single, 'last_seen', last_seen) \
            .property(Cardinality.single, 'expiration', expiration) \
            .sideEffect(
                __.addE("universe_of")
                .from_(
                    __.V()
                    .hasLabel('Universe')
                    .has('namespace', CURRENT_UNIVERSE.namespace)
                    .has('version', CURRENT_UNIVERSE.version.int_version)
                )
            ) \
            .elementMap() \
            .next()
        created_assets.append(DbAsset.from_vasset(vasset))

    created_assets.sort(key=lambda x: x.vid)

    yield created_assets


@pytest.fixture
def init_new_universe_assets(g, new_universe):
    """Creates an initial set of assets and yields a ``DbAsset`` list.  They
    can be used to test the ``InventoryClient``."""
    # (type, identifier, first_seen, last_seen, expiration)
    assets = [
        (
            'type0', 'identifier0',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        ),
        (
            'type0', 'identifier1',
            '2021-07-01T01:00:00+00:00',
            '2021-07-07T01:00:00+00:00',
            '2021-07-14T01:00:00+00:00',
        )
    ]
    create_universe(g, new_universe)

    # Add assets.
    created_assets = []
    for asset in assets:
        asset_type = asset[0]
        asset_identifier = asset[1]
        first_seen = datetime.fromisoformat(asset[2])
        last_seen = datetime.fromisoformat(asset[3])
        expiration = datetime.fromisoformat(asset[4])
        vasset = g.addV('Asset') \
            .property(T.id, str(uuid.uuid4())) \
            .property(Cardinality.single, 'type', asset_type) \
            .property(Cardinality.single, 'identifier', asset_identifier) \
            .property(Cardinality.single, 'first_seen', first_seen) \
            .property(Cardinality.single, 'last_seen', last_seen) \
            .property(Cardinality.single, 'expiration', expiration) \
            .sideEffect(
                __.addE("universe_of")
                .from_(
                    __.V()
                    .hasLabel('Universe')
                    .has('namespace', new_universe.namespace)
                    .has('version', new_universe.version.int_version)
                )
            ) \
            .elementMap() \
            .next()
        created_assets.append(DbAsset.from_vasset(vasset))

    created_assets.sort(key=lambda x: x.vid)

    yield created_assets


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
    form ``{vid0: [DbParentOf], vid1: [DbParentOf]}``.  They can be used to
    test the ``InventoryClient``."""
    edges = {
        # child_idx: [(parent_idx, first_seen, last_seen, expiration)]
        0: [
            (
                2,
                '2021-07-01T01:00:00+00:00',
                '2021-07-07T01:00:00+00:00',
                '2021-07-14T01:00:00+00:00',
            ),
            (
                3,
                '2021-07-01T01:00:00+00:00',
                '2021-07-07T01:00:00+00:00',
                '2021-07-14T01:00:00+00:00',
            ),
            (
                4,
                '2021-07-01T01:00:00+00:00',
                '2021-07-07T01:00:00+00:00',
                '2021-07-14T01:00:00+00:00',
            ),
            (
                5,
                '2021-07-01T01:00:00+00:00',
                '2021-07-07T01:00:00+00:00',
                '2021-07-14T01:00:00+00:00',
            ),
        ],
        1: [
            (
                6,
                '2021-07-01T01:00:00+00:00',
                '2021-07-07T01:00:00+00:00',
                '2021-07-14T01:00:00+00:00',
            ),
            (
                7,
                '2021-07-01T01:00:00+00:00',
                '2021-07-07T01:00:00+00:00',
                '2021-07-14T01:00:00+00:00',
            ),
            (
                8,
                '2021-07-01T01:00:00+00:00',
                '2021-07-07T01:00:00+00:00',
                '2021-07-14T01:00:00+00:00',
            ),
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
                .property(T.id, str(uuid.uuid4())) \
                .property('first_seen', first_seen) \
                .property('last_seen', last_seen) \
                .property('expiration', expiration) \
                .elementMap() \
                .next()

            dbparents[child_vid].append(DbParentOf.from_eparentof(eparentof))

        dbparents[child_vid].sort(key=lambda x: x.eid)

    yield dbparents


@pytest.fixture
def init_api_parents(init_parents):
    """Converts the ``DbParentOf`` lists created by ``init_parents`` into lists
    of dicts that can be used to test the responses of the API endpoints."""
    api_parents = {}
    for k, v in init_parents.items():
        api_parents[k] = [
            ParentOfResp.from_dbparentof(po).__dict__ for po in v
        ]

    yield api_parents


# Owners.


@pytest.fixture
def init_owners(g, init_teams, init_assets):
    """Creates an initial set of ``owns`` edges and yields a dict of the form
    ``{vid0: [DbOwns], vid1: [DbOwns]}``. They can be used to test the
    ``InventoryClient``."""
    edges = {
        # asset_idx: [(asset_idx, start_time, end_time)]
        0: [
            (1, '2021-07-01T01:00:00+00:00', '2021-07-07T01:00:00+00:00'),
            (2, '2021-07-01T01:00:00+00:00', '2021-07-07T01:00:00+00:00'),
            (3, '2021-07-01T01:00:00+00:00', '2021-07-07T01:00:00+00:00'),
        ],
        1: [
            (4, '2021-07-01T01:00:00+00:00', '2021-07-07T01:00:00+00:00'),
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
                .property(T.id, str(uuid.uuid4())) \
                .property('start_time', start_time) \
                .property('end_time', end_time) \
                .elementMap() \
                .next()

            dbowners[asset_vid].append(DbOwns.from_eowns(eowns))

        dbowners[asset_vid].sort(key=lambda x: x.eid)

    yield dbowners


@pytest.fixture
def init_api_owners(init_owners):
    """Converts the ``DbOwns`` lists created by ``init_owners`` into lists
    of dicts that can be used to test the responses of the API endpoints."""
    api_owners = {}
    for k, v in init_owners.items():
        api_owners[k] = [
            OwnsResp.from_dbowns(o).__dict__ for o in v
        ]

    yield api_owners


def create_universe(g, universe):
    """Creates a new  asset inventory ``Universe`` vertex"""
    return g \
        .addV("Universe") \
        .property(T.id, str(uuid.uuid4())) \
        .property(
                    Cardinality.single, 'namespace',
                    universe.namespace
                ) \
        .property(
                    Cardinality.single, 'version',
                    universe.version.int_version
        ).next()
