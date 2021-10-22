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
from graph_asset_inventory_api.inventory.universe import CurrentUniverse


class InventoryTraversal(GraphTraversal):
    """Graph Traversal for the Asset Inventory."""

    # Teams.

    def is_team(self):
        """Filters vertices of type ``Team``."""
        return self.hasLabel('Team')

    def is_team_identifier(self, identifier):
        """Filters vertices of type ``Team`` with a specific ``identifier``."""
        return self.is_team().has('identifier', identifier)

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

    # Universe

    def link_to_universe(self):
        """Creates an edge from the vertices in the transversal to the current
        universe vertex"""
        return self \
            .sideEffect(
              __.identity().addE("universe").from_(__.V(CurrentUniverse.id()))
            )


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


class InventoryTraversalSource(GraphTraversalSource):
    """Graph Traversal Source for the Asset Inventory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph_traversal = InventoryTraversal

    # Teams.

    def teams(self):
        """Returns all the ``Team`` vertices."""
        return self.V().is_team()

    def team(self, vid):
        """Returns a ``Team`` vertex with a given vertex id ``vid``."""
        return self.V(vid).is_team()

    def team_identifier(self, identifier):
        """Returns a ``Team`` vertex with a given ``identifier``."""
        return self.V().is_team_identifier(identifier)

    def add_team(self, team):
        """Creates a new ``Team`` vertex."""
        return self \
            .team_identifier(team.identifier) \
            .fold() \
            .coalesce(
                # The team exists.
                __.unfold()
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(True)),
                # The team does not exist.
                __.addV('Team')
                .property(T.id, str(uuid.uuid4()))
                .property(Cardinality.single, 'identifier', team.identifier)
                .property(Cardinality.single, 'name', team.name)
                .link_to_universe()
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
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

    def assets(self, asset_type=None):
        """Returns all the ``Asset`` vertices."""
        assets = self.V().is_asset()
        if asset_type is None:
            return assets
        return assets.has('type', asset_type)

    def asset(self, vid):
        """Returns an ``Asset`` vertex with a given vertex id ``vid``."""
        return self.V(vid).is_asset()

    def asset_id(self, asset_id):
        """Returns an ``Asset`` vertex with a given ``type`` and
        ``identifier``."""
        return self.V().is_asset_id(asset_id)

    def add_asset(self, asset, expiration, timestamp):
        """Creates a new ``Asset`` vertex."""
        return self \
            .asset_id(asset.asset_id) \
            .fold() \
            .coalesce(
                # The asset exists.
                __.unfold()
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
                .link_to_universe()
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

    def set_asset(self, asset, expiration, timestamp):
        """Updates an ``Asset`` vertex with the specified time attributes. If
        the vertex does not exist, it is created.

        The time attributes are updated following these rules:

        - If ``timestamp < first_seen``, then ``first_seen = timestamp``.
        - If ``timestamp > last_seen``, then ``last_seen = timestamp`` and
          ``expiration = expiration``.
        - Otherwise, nothing is modified."""
        return self \
            .asset_id(asset.asset_id) \
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
                .link_to_universe()
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

    def ensure_universe(self):
        """Creates a new  asset inventory ``Universe`` vertex, if it doesn't
        exist, and returns its id"""
        universe = self \
            .V(CurrentUniverse.id()) \
            .fold() \
            .coalesce(
                # The universe vertex already exists.
                __.unfold()
                .project('id')
                .by(__.id()),
                # The universe vertex does not exist.
                __.addV("Universe")
                .property(T.id, CurrentUniverse.id())
                .property(
                          Cardinality.single, 'namespace',
                          CurrentUniverse.namespace
                         )
                .property(
                          Cardinality.single, 'version',
                          CurrentUniverse.version.int_version
                        )
                .project('id')
                .by(__.id()),
            ).next()
        return universe["id"]

    def universe_of(self, vid):
        """Returns a ``Universe`` vertex associated with the vertex identified
        by the vertex id ``vid``."""
        ret = self \
            .V(vid).inE() \
            .hasLabel('universe') \
            .outV()
        return ret

    def current_universe(self):
        """Returns the ``Universe`` that corresponds to the CurrentUniverse
        class"""
        ret = self.V(CurrentUniverse.id())
        return ret
