from gremlin_python.process.graph_traversal import (
    GraphTraversal,
    GraphTraversalSource,
    __,
)


class SecurityGraphTraversal(GraphTraversal):
    def is_team(self):
        return self.hasLabel('Team')

    def is_team_identifier(self, identifier):
        return self.is_team().has('identifier', identifier)


class SecurityGraphTraversalSource(GraphTraversalSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph_traversal = SecurityGraphTraversal

    def teams(self):
        return self.V().is_team()

    def team(self, vid):
        return self.V(vid).is_team()

    def team_identifier(self, identifier):
        return self.V().is_team_identifier(identifier)

    def add_team(self, team):
        return self \
            .team_identifier(team.identifier) \
            .fold() \
            .coalesce(
                __.unfold(),
                __.addV('Team').property('identifier', team.identifier),
            ) \
            .property('name', team.name)
