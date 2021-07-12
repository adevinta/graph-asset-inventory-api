"""This modules provides the class ``InventoryClient`` that provides access to
the Asset Inventory."""

from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import Order
from gremlin_python.driver.driver_remote_connection import (
    DriverRemoteConnection,
)

from graph_asset_inventory_api.inventory import (
    DbTeam,
    InventoryError,
    NotFoundError,
    ConflictError,
    InconsistentStateError,
)
from graph_asset_inventory_api.inventory.dsl import (
    InventoryTraversalSource,
)


class InventoryClient:
    """Client that provides access to the Asset Inventory."""

    def __init__(self, neptune_endpoint):
        self._conn = DriverRemoteConnection(neptune_endpoint, 'g')
        self._g = traversal(InventoryTraversalSource).withRemote(self._conn)

    def close(self):
        """Releases the resources being used by the client, for instance the
        graph connection."""
        self._conn.close()

    def g(self):
        """Returns the graph traversal source."""
        return self._g

    def teams(self, page_idx=None, page_size=100):
        """Returns all teams if ``page_idx`` is None. Otherwise it returns the
        page of teams with index ``page_idx`` and size ``page_size``. By
        default, the page size is 100 items."""

        vteams = self._g \
            .teams()

        if page_idx is not None:
            offset = page_idx * page_size
            vteams = vteams \
                .order() \
                .by('identifier', Order.asc) \
                .range(offset, offset + page_size) \

        vteams = vteams \
            .elementMap() \
            .toList()

        teams = [DbTeam.from_vteam(vt) for vt in vteams]
        return teams

    def team(self, vid):
        """Returns the team with vertex ID ``vid``. If the team does not exist,
        a ``NotFoundError`` exception is raised."""
        vteams = self._g \
            .team(vid) \
            .elementMap() \
            .toList()

        if len(vteams) == 0:
            raise NotFoundError(vid)
        if len(vteams) > 1:
            raise InconsistentStateError('duplicated team')

        return DbTeam.from_vteam(vteams[0])

    def team_identifier(self, identifier):
        """Returns the team with identifier ``identifier``. If the team does
        not exist, a ``NotFoundError`` exception is raised."""
        vteams = self._g \
            .team_identifier(identifier) \
            .elementMap() \
            .toList()

        if len(vteams) == 0:
            raise NotFoundError(identifier)
        if len(vteams) > 1:
            raise InconsistentStateError('duplicated team')

        return DbTeam.from_vteam(vteams[0])

    def add_team(self, team):
        """Create a new team. If the team already exists, a ``ConflictError``
        exception is raised."""
        vteams = self._g.add_team(team).toList()

        if len(vteams) == 0:
            raise InventoryError('team was not created')
        if len(vteams) > 1:
            raise InconsistentStateError('duplicated team')
        if vteams[0]['exists']:
            raise ConflictError(team.identifier)

        return DbTeam.from_vteam(vteams[0]['vertex'])

    def update_team(self, vid, team):
        """Updates the team with vertex ID ``vid``. If the team does not exist,
        a ``NotFoundError`` exception is raised."""
        vteams = self._g.update_team(vid, team).toList()

        if len(vteams) == 0:
            raise NotFoundError(vid)
        if len(vteams) > 1:
            raise InconsistentStateError('duplicated team')

        return DbTeam.from_vteam(vteams[0])

    def drop_team(self, vid):
        """Deletes the team with vertex ID ``vid``. If the team does not exist,
        a ``NotFoundError`` exception is raised."""
        vteams = self._g \
            .team(vid) \
            .toList()

        if len(vteams) == 0:
            raise NotFoundError(vid)
        if len(vteams) > 1:
            raise InconsistentStateError('duplicated team')

        self._g.team(vid).drop().iterate()
