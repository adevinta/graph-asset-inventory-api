"""Gremlin DSL for the Asset Inventory."""

import uuid

from gremlin_python.process.traversal import P
from gremlin_python.process.graph_traversal import (
    GraphTraversal,
    GraphTraversalSource,
    __ as AnonymousTraversal,
)
from gremlin_python.process.traversal import (
    T,
    Cardinality,
    Bytecode,
)


class InventoryTraversal(GraphTraversal):
    """Graph Traversal for the Asset Inventory."""

    # Teams.

    def is_team(self):
        """Filters vertices of type ``Team``."""
        return self.hasLabel('Team')

    def is_team_identifier(self, identifier):
        """Filters vertices of type ``Team`` with a specific ``identifier``."""
        return self.is_team().has('identifier', identifier)

    def add_team(self, team, universe):
        """Creates a new Team vertex, links it to the current universe and
        returns the newly created vertex."""
        return self \
            .addV('Team') \
            .property(T.id, str(uuid.uuid4())) \
            .property(Cardinality.single, 'identifier', team.identifier) \
            .property(Cardinality.single, 'name', team.name) \
            .link_to_universe(universe)

    # Assets.

    def is_asset(self):
        """Filters vertices of type ``Asset``."""
        return self.hasLabel('Asset')

    def is_asset_id(self, asset_id):
        """Filters vertices of type ``Asset`` with a specific ``type`` and
        ``identifier``."""
        return self \
            .is_asset() \
            .has('type', asset_id.type) \
            .has('identifier', asset_id.identifier)

    def add_asset(
          self,
          asset,
          expiration,
          timestamp,
          universe
    ):
        """Creates a new Asset vertex, links it to the given ``universe`` and
        returns the newly created vertex."""
        return self \
            .addV('Asset') \
            .property(T.id, str(uuid.uuid4())) \
            .property(Cardinality.single, 'type', asset.asset_id.type) \
            .property(
                Cardinality.single,
                'identifier',
                asset.asset_id.identifier,
            ) \
            .property(Cardinality.single, 'first_seen', timestamp) \
            .property(Cardinality.single, 'last_seen', timestamp) \
            .property(Cardinality.single, 'expiration', expiration) \
            .link_to_universe(universe)

    # Parents.

    def is_parent_of(self):
        """Filters edges of type ``parent_of``."""
        return self.hasLabel('parent_of')

    # Owners.

    def is_owns(self):
        """Filters edges of type ``owns``."""
        return self.hasLabel('owns')

    def properties_owns(self, start_time, end_time=None):
        """Sets the properties for edges of type ``owns``. If ``end_time`` is
        ``None``, the property is not set."""
        ret = self.property('start_time', start_time)

        if end_time is None:
            ret = ret.sideEffect(__.properties('end_time').drop())
        else:
            ret = ret.property('end_time', end_time)

        return ret

    # Universe.

    def link_to_universe(self, universe):
        """Creates an edge from the vertices in the transversal to the current
        universe vertex."""
        return self \
            .sideEffect(
              __.addE("universe_of")
              .from_(__.V().is_universe_obj(universe))
            )

    def is_universe(self):
        """Filters the vertices that are Universes."""
        return self \
            .hasLabel('Universe')

    def is_universe_obj(self, universe):
        """Filters the Asset Inventory Universe with a given version and
        namespace."""
        return self \
            .is_universe() \
            .has('namespace', universe.namespace) \
            .has('version', universe.version.int_version)

    def linked_universe(self):
        """Returns the ``Universe`` associated with a vertex."""
        return self \
            .inE() \
            .is_universe_of() \
            .outV()

    def is_linked_to_universe(self, universe):
        """Returns the ``Universe`` vertex associated with a vertex only if it
        matches the specified universe."""
        return self \
            .linked_universe() \
            .is_universe_obj(universe)

    def is_universe_of(self):
        """Filters edges of type ``universe_of``."""
        return self.hasLabel('universe_of')


class __(AnonymousTraversal):
    """Anonymous Traversal for the Asset Inventory."""

    graph_traversal = InventoryTraversal

    # Teams.

    @classmethod
    def is_team(cls, *args):
        """Filters vertices of type ``Team``."""
        return cls.graph_traversal(None, None, Bytecode()).is_team(*args)

    @classmethod
    def is_team_identifier(cls, *args):
        """Filters vertices of type ``Team`` with a specific ``identifier``."""
        return cls.graph_traversal(
            None, None, Bytecode()).is_team_identifier(*args)

    @classmethod
    def add_team(cls, *args):
        """Creates a new Team vertex, links it to the specified universe and
        returns the newly created vertex."""
        return cls.graph_traversal(
            None, None, Bytecode()).add_team(*args)

    # Assets.

    @classmethod
    def is_asset(cls, *args):
        """Filters vertices of type ``Asset``."""
        return cls.graph_traversal(None, None, Bytecode()).is_asset(*args)

    @classmethod
    def is_asset_id(cls, *args):
        """Filters vertices of type ``Asset`` with a specific ``type`` and
        ``identifier``."""
        return cls.graph_traversal(None, None, Bytecode()).is_asset_id(*args)

    @classmethod
    def add_asset(cls, *args):
        """Creates a new Asset vertex, links it to the specified universe and
        returns the newly created vertex."""
        return cls.graph_traversal(
            None, None, Bytecode()).add_asset(*args)

    # Parents.

    @classmethod
    def is_parent_of(cls, *args):
        """Filters edges of type ``parent_of``."""
        return cls.graph_traversal(None, None, Bytecode()).is_parent_of(*args)

    # Owners.

    @classmethod
    def is_owns(cls, *args):
        """Filters edges of type ``owns``."""
        return cls.graph_traversal(None, None, Bytecode()).is_owns(*args)

    @classmethod
    def properties_owns(cls, *args):
        """Sets the properties for edges of type ``owns``. If ``end_time`` is
        ``None``, the property is not set."""
        return cls.graph_traversal(
            None, None, Bytecode()).properties_owns(*args)

    # Universe.

    @classmethod
    def link_to_universe(cls, *args):
        """Creates an edge from the vertices in the transversal to the current
        universe vertex."""
        return cls.graph_traversal(
            None, None, Bytecode()).link_to_universe(*args)

    @classmethod
    def is_universe(cls, *args):
        """Filters the vertices that are Asset Inventory Universes."""
        return cls.graph_traversal(
            None, None, Bytecode()).is_universe(*args)

    @classmethod
    def is_universe_obj(cls, *args):
        """Filters the Asset Inventory Universe with a given version and
        namespace."""
        return cls.graph_traversal(
            None, None, Bytecode()).is_universe(*args)

    @classmethod
    def is_linked_to_universe(cls, *args):
        """Returns the ``Universe`` vertex associated with a vertex only if it
        matches the specified universe."""
        return cls.graph_traversal(
            None, None, Bytecode()).is_linked_to_universe(*args)

    @classmethod
    def is_universe_of(cls):
        """Filters edges of type ``universe_of``."""
        return cls.graph_traversal(
            None, None, Bytecode()).is_universe_of()


class InventoryTraversalSource(GraphTraversalSource):
    """Graph Traversal Source for the Asset Inventory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph_traversal = InventoryTraversal

    # Teams.

    def teams(self, universe, team_identifier=None):
        """Returns all the ``Team`` vertices belonging to the given
        universe."""
        teams = self \
            .V() \
            .is_team() \
            .where(__.is_linked_to_universe(universe))

        if team_identifier is not None:
            teams = teams.has('identifier', team_identifier)

        return teams

    def team(self, vid):
        """Returns a ``Team`` vertex with a given vertex id ``vid``."""
        return self.V(vid).is_team()

    def team_identifier(self, identifier, universe):
        """Returns a ``Team`` vertex with a given ``identifier`` belonging to
        the given universe."""
        return self \
            .V() \
            .is_team_identifier(identifier) \
            .where(__.is_linked_to_universe(universe))

    def add_team(self, team, universe):
        """Creates a new ``Team`` vertex and links it the specified
        ``universe``"""
        return self \
            .team_identifier(team.identifier, universe) \
            .fold() \
            .coalesce(
                # The team exists.
                __.unfold()
                .choose(
                    __.is_linked_to_universe(universe),
                    # The team exists and is linked to the universe.
                    __.project('vertex', 'exists')
                    .by(__.identity().elementMap())
                    .by(__.constant(True)),
                    # Even though the team exists, it is not linked to the
                    # universe so we create a new team and link it to
                    # the proper universe.
                    __.add_team(team, universe)
                    .project('vertex', 'exists')
                    .by(__.identity().elementMap())
                    .by(__.constant(False)),
                ),
                # The team does not exist in any universe.
                __.add_team(team, universe)
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False))
            )

    def update_team(self, vid, team):
        """Updates the ``Team`` vertex with id ``vid``."""
        return self \
            .team(vid) \
            .is_team_identifier(team.identifier) \
            .property(Cardinality.single, 'name', team.name) \
            .elementMap()

    def drop_team(self, vid):
        """Deletes the ``Team`` vertex with id ``vid``."""
        return self \
            .team(vid) \
            .sideEffect(__.drop()) \
            .count()

    # Assets.

    def assets(self, universe, asset_type=None, asset_identifier=None):
        """Returns all the ``Asset`` vertices that belong to a ``Universe``."""
        assets = self \
            .V() \
            .is_asset() \
            .where(__.is_linked_to_universe(universe))

        if asset_type is not None:
            assets = assets.has('type', asset_type)

        if asset_identifier is not None:
            assets = assets.has('identifier', asset_identifier)

        return assets

    def asset(self, vid):
        """Returns an ``Asset`` vertex with a given vertex id ``vid``."""
        return self.V(vid).is_asset()

    def asset_id(self, asset_id, universe):
        """Returns an ``Asset`` vertex with a given ``type`` and ``identifier``
        if it exists and it's associated the with the given ``universe``."""
        return self \
            .V() \
            .is_asset_id(asset_id) \
            .where(__.is_linked_to_universe(universe))

    def add_asset(
        self,
        asset,
        expiration,
        timestamp,
        universe
    ):
        """Creates a new ``Asset`` vertex, links it to the specified universe
        and returns the newly created vertex."""
        return self \
            .asset_id(asset.asset_id, universe) \
            .fold() \
            .coalesce(
                # The asset exists.
                __.unfold()
                .choose(
                    __.is_linked_to_universe(universe),
                    # The Asset exists and is linked to the universe.
                    __.project('vertex', 'exists')
                    .by(__.identity().elementMap())
                    .by(__.constant(True)),
                    # Even though the asset exists, it is not linked to the
                    # universe so we create a new asset and link it to the
                    # proper universe.
                    __.add_asset(asset, expiration, timestamp, universe)
                    .project('vertex', 'exists')
                    .by(__.identity().elementMap())
                    .by(__.constant(False)),
                ),
                # The asset does not exist in any universe.
                __.add_asset(asset, expiration, timestamp, universe)
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

    def update_asset(self, vid, asset, expiration, timestamp):
        """Updates an ``Asset`` vertex with the specified time attributes.

        The time attributes are updated following these rules:

        - If ``timestamp < first_seen``, then ``first_seen = timestamp``.
        - If ``timestamp > last_seen``, then ``last_seen = timestamp`` and
          ``expiration = expiration``.
        - Otherwise, nothing is modified."""
        return self \
            .asset(vid) \
            .is_asset_id(asset.asset_id) \
            .choose(
                __.values('first_seen').is_(P.gt(timestamp)),
                __.property(Cardinality.single, 'first_seen', timestamp),
                __.identity(),
            ) \
            .choose(
                __.values('last_seen').is_(P.lt(timestamp)),
                __.property(Cardinality.single, 'last_seen', timestamp)
                  .property(Cardinality.single, 'expiration', expiration),
                __.identity(),
            ) \
            .elementMap()

    def set_asset(
          self,
          asset,
          expiration,
          timestamp,
          universe
    ):
        """Updates an ``Asset`` vertex with the specified time attributes. If
        the vertex does not exist or it's not associated with the given
        universe, it is created.

        The time attributes are updated following these rules:

        - If ``timestamp < first_seen``, then ``first_seen = timestamp``.
        - If ``timestamp > last_seen``, then ``last_seen = timestamp`` and
          ``expiration = expiration``.
        - Otherwise, nothing is modified."""
        return self \
            .asset_id(asset.asset_id, universe) \
            .fold() \
            .coalesce(
                # The asset exists.
                __.unfold()
                .choose(
                    __.values('first_seen').is_(P.gt(timestamp)),
                    __.property(Cardinality.single, 'first_seen', timestamp),
                    __.identity(),
                )
                .choose(
                    __.values('last_seen').is_(P.lt(timestamp)),
                    __.property(Cardinality.single, 'last_seen', timestamp)
                      .property(Cardinality.single, 'expiration', expiration),
                    __.identity(),
                )
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(True)),
                # The asset does not exist.
                __.addV('Asset')
                .property(T.id, str(uuid.uuid4()))
                .property(Cardinality.single, 'type', asset.asset_id.type)
                .property(
                    Cardinality.single,
                    'identifier',
                    asset.asset_id.identifier,
                )
                .property(Cardinality.single, 'first_seen', timestamp)
                .property(Cardinality.single, 'last_seen', timestamp)
                .property(Cardinality.single, 'expiration', expiration)
                .link_to_universe(universe)
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

    def drop_asset(self, vid):
        """Deletes the ``Asset`` vertex with id ``vid``."""
        return self \
            .asset(vid) \
            .sideEffect(__.drop()) \
            .count()

    # Parents.

    def parent_of(self, eid):
        """Returns a ``parent_of`` edge with a given edge id ``eid``."""
        return self.E(eid).is_parent_of()

    def parents(self, asset_vid):
        """Returns the incoming ``parent_of`` edges of the Asset vertex with ID
        ``vid``."""
        return self \
            .asset(asset_vid) \
            .inE() \
            .is_parent_of()

    def set_parent_of(self, parentof, expiration, timestamp):
        """Updates a ``parent_of`` edge with the specified time attributes. If
        the edge does not exist, it is created.

        The time attributes are updated following these rules:

        - If ``timestamp < first_seen``, then ``first_seen = timestamp``.
        - If ``timestamp > last_seen``, then ``last_seen = timestamp`` and
          ``expiration = expiration``.
        - Otherwise, nothing is modified."""
        return self \
            .V(parentof.parent_vid) \
            .is_asset() \
            .as_('parent_v') \
            .V(parentof.child_vid) \
            .is_asset() \
            .coalesce(
                # The edge exists.
                __.inE('parent_of').filter(
                    __.outV().id().is_(parentof.parent_vid))
                .choose(
                    __.values('first_seen').is_(P.gt(timestamp)),
                    __.property('first_seen', timestamp),
                    __.identity(),
                )
                .choose(
                    __.values('last_seen').is_(P.lt(timestamp)),
                    __.property('last_seen', timestamp) \
                      .property('expiration', expiration),
                    __.identity(),
                )
                .project('edge', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(True)),
                # The edge does not exist.
                __.addE('parent_of').from_('parent_v')
                .property(T.id, str(uuid.uuid4()))
                .property('first_seen', timestamp)
                .property('last_seen', timestamp)
                .property('expiration', expiration)
                .project('edge', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

    def drop_parent_of(self, eid):
        """Deletes the ``parent_of`` edge with id ``eid``."""
        return self \
            .parent_of(eid) \
            .sideEffect(__.drop()) \
            .count()

    # Owners.

    def owns(self, eid):
        """Returns an ``owns`` edge with a given edge id ``eid``."""
        return self.E(eid).is_owns()

    def owners(self, asset_vid):
        """Returns the incoming ``owns`` edges of the Asset vertex with ID
        ``vid``."""
        return self \
            .asset(asset_vid) \
            .inE() \
            .is_owns()

    def set_owns(self, owns_, start_time, end_time=None):
        """Updates an ``owns`` edge with the specified time attributes. If
        the edge does not exist, it is created."""
        return self \
            .V(owns_.team_vid) \
            .is_team() \
            .as_('team_v') \
            .V(owns_.asset_vid) \
            .is_asset() \
            .coalesce(
                # The edge exists.
                __.inE('owns').filter(
                    __.outV().id().is_(owns_.team_vid))
                .properties_owns(start_time, end_time)
                .project('edge', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(True)),
                # The edge does not exist.
                __.addE('owns').from_('team_v')
                .property(T.id, str(uuid.uuid4()))
                .properties_owns(start_time, end_time)
                .project('edge', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

    def drop_owns(self, eid):
        """Deletes the ``owns`` edge with id ``eid``."""
        return self \
            .owns(eid) \
            .sideEffect(__.drop()) \
            .count()

    # Universe

    def ensure_universe(self, universe):
        """Creates a new  asset inventory ``Universe`` vertex, if it doesn't
        exist, and returns its id."""
        return self \
            .V() \
            .is_universe_obj(universe) \
            .fold() \
            .coalesce(
                # The universe vertex already exists.
                __.unfold()
                .elementMap(),
                # The universe vertex does not exist.
                __.addV("Universe")
                .property(T.id, str(uuid.uuid4()))
                .property(
                    Cardinality.single,
                    'namespace',
                    universe.namespace
                )
                .property(
                    Cardinality.single,
                    'version',
                    universe.version.int_version
                )
                .elementMap(),
            )

    def linked_universe(self, vid):
        """Returns a ``Universe`` vertex associated with the vertex identified
        by the vertex id ``vid``."""
        ret = self \
            .V(vid) \
            .linked_universe()
        return ret

    def universe(self, universe):
        """Returns the ``Universe`` vertex that corresponds to specified
        universe."""
        return self\
            .V() \
            .is_universe_obj(universe)
