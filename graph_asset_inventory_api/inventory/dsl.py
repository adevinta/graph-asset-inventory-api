"""Gremlin DSL for the Asset Inventory."""

from gremlin_python.process.traversal import P
from gremlin_python.process.graph_traversal import (
    GraphTraversal,
    GraphTraversalSource,
    __,
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
        """Filsters edges of type ``parent_of``."""
        return self.hasLabel('parent_of')

    # Owners.

    def is_owns(self):
        """Filsters edges of type ``owns``."""
        return self.hasLabel('owns')


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
                .property('identifier', team.identifier)
                .property('name', team.name)
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

    def update_team(self, vid, team):
        """Updates the ``Team`` vertex with id ``vid``."""
        return self \
            .team(vid) \
            .property('identifier', team.identifier) \
            .property('name', team.name) \
            .elementMap()

    # Assets.

    def assets(self):
        """Returns all the ``Asset`` vertices."""
        return self.V().is_asset()

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
                .property('type', asset.asset_id.type)
                .property('identifier', asset.asset_id.identifier)
                .property('first_seen', timestamp)
                .property('last_seen', timestamp)
                .property('expiration', expiration)
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

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
                    __.property('first_seen', timestamp),
                    __.identity(),
                )
                .choose(
                    __.values('last_seen').is_(P.lt(timestamp)),
                    __.property('last_seen', timestamp) \
                      .property('expiration', expiration),
                    __.identity(),
                )
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(True)),
                # The asset does not exist.
                __.addV('Asset')
                .property('type', asset.asset_id.type)
                .property('identifier', asset.asset_id.identifier)
                .property('first_seen', timestamp)
                .property('last_seen', timestamp)
                .property('expiration', expiration)
                .project('vertex', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

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
            .asset(parentof.child_vid) \
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
                __.addE('parent_of').from_(__.V(parentof.parent_vid))
                .property('first_seen', timestamp)
                .property('last_seen', timestamp)
                .property('expiration', expiration)
                .project('edge', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )

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

    def set_owns(self, owns_, start_time, end_time):
        """Updates an ``owns`` edge with the specified time attributes. If
        the edge does not exist, it is created."""
        return self \
            .asset(owns_.asset_vid) \
            .coalesce(
                # The edge exists.
                __.inE('owns').filter(
                    __.outV().id().is_(owns_.team_vid))
                .property('start_time', start_time)
                .property('end_time', end_time)
                .project('edge', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(True)),
                # The edge does not exist.
                __.addE('owns').from_(__.V(owns_.team_vid))
                .property('start_time', start_time)
                .property('end_time', end_time)
                .project('edge', 'exists')
                .by(__.identity().elementMap())
                .by(__.constant(False)),
            )
