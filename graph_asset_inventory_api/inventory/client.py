from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import Order
from gremlin_python.driver.driver_remote_connection import (
    DriverRemoteConnection,
)

from graph_asset_inventory_api.inventory.types import (
    DbTeam,
    InventoryException,
    NotFoundException,
    InconsistentStateException,
)
from graph_asset_inventory_api.inventory.dsl import (
    SecurityGraphTraversalSource,
)


class InventoryClient:
    def __init__(self, neptune_endpoint):
        self._conn = DriverRemoteConnection(neptune_endpoint, 'g')
        self._g = traversal(SecurityGraphTraversalSource) \
            .withRemote(self._conn)

    def close(self):
        self._conn.close()

    def g(self):
        return self._g

    def teams(self):
        vteams = self._g.teams().elementMap().toList()
        teams = [DbTeam.from_vteam(vt) for vt in vteams]
        return teams

    def teams_page(self, page, size):
        offset = page * size
        vteams = self._g \
            .teams() \
            .order() \
            .by('identifier', Order.asc) \
            .range(offset, offset + size) \
            .elementMap() \
            .toList()
        teams = [DbTeam.from_vteam(vt) for vt in vteams]
        return teams

    def team(self, vid):
        vteams = self._g \
            .team(vid) \
            .elementMap() \
            .toList()

        if len(vteams) == 0:
            raise NotFoundException
        if len(vteams) > 1:
            raise InconsistentStateException('duplicated team')

        return DbTeam.from_vteam(vteams[0])

    def team_identifier(self, identifier):
        vteams = self._g \
            .team_identifier(identifier) \
            .elementMap() \
            .toList()

        if len(vteams) == 0:
            raise NotFoundException
        if len(vteams) > 1:
            raise InconsistentStateException('duplicated team')

        return DbTeam.from_vteam(vteams[0])

    def add_team(self, team):
        vteams = self._g.add_team(team).elementMap().toList()

        if len(vteams) == 0:
            raise InventoryException('team was not created')
        if len(vteams) > 1:
            raise InconsistentStateException('duplicated team')

        return DbTeam.from_vteam(vteams[0])

    def drop_team(self, vid):
        self._g.team(vid).drop().iterate()
