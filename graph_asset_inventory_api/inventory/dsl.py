"""Gremlin DSL for the Asset Inventory."""

from gremlin_python.process.graph_traversal import (
    GraphTraversal,
    GraphTraversalSource,
    __,
)


class InventoryTraversal(GraphTraversal):
    """Graph Traversal for the Asset Inventory."""

    def is_team(self):
        """Filters vertices of type ``Team``."""
        return self.hasLabel('Team')

    def is_team_identifier(self, identifier):
        """Filters vertices of type ``Team`` with a specific ``identifier``."""
        return self.is_team().has('identifier', identifier)


class InventoryTraversalSource(GraphTraversalSource):
    """Graph Traversal Source for the Asset Inventory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph_traversal = InventoryTraversal

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
        """Create a new ``Team`` vertex. If the vertex already exists, its name
        property is updated."""
        return self \
            .team_identifier(team.identifier) \
            .fold() \
            .coalesce(
                __.unfold(),
                __.addV('Team').property('identifier', team.identifier),
            ) \
            .property('name', team.name)
