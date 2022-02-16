"""This modules provides the class ``InventoryClient`` that provides access to
the Asset Inventory."""

from datetime import (
    datetime,
    timezone,
)

from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import (
    T,
    Order,
)

from graph_asset_inventory_api.inventory import (
    DbTeam,
    DbAsset,
    DbParentOf,
    DbOwns,
    DbUniverse,
    InventoryError,
    NotFoundError,
    ConflictError,
    InconsistentStateError,
)
from graph_asset_inventory_api.inventory.dsl import (
    InventoryTraversalSource,
)
from graph_asset_inventory_api import gremlin
from graph_asset_inventory_api.inventory import CURRENT_UNIVERSE


class InventoryClient:
    """Client that provides access to the Asset Inventory.

    This Client is concurrent-safe in terms of DB integrity."""

    def __init__(self, gremlin_endpoint, auth_mode='none'):
        self._conn = gremlin.get_connection(gremlin_endpoint, auth_mode)
        self._g = traversal(InventoryTraversalSource).withRemote(self._conn)

    def close(self):
        """Releases the resources being used by the client, for instance the
        graph connection."""
        self._conn.close()

    def g(self):
        """Returns the graph traversal source."""
        return self._g

    # Teams.

    def teams(
        self,
        page_idx=None,
        page_size=100,
        team_identifier=None,
        universe=CURRENT_UNIVERSE,
    ):
        """Returns all teams associated with the given ``universe`` (filtered
        by ``identifier`` if specified) if ``page_idx`` is None. Otherwise it
        returns the page of teams with index ``page_idx`` and size
        ``page_size``. By default, the page size is 100 items."""

        vteams = self._g \
            .teams(universe, team_identifier)

        if page_idx is not None:
            offset = page_idx * page_size
            vteams = vteams \
                .order() \
                .by(T.id, Order.asc) \
                .range(offset, offset + page_size)

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

    def team_identifier(self, identifier, universe=CURRENT_UNIVERSE):
        """Returns the team with identifier ``identifier`` of the specified
        ``universe``. If the team does not exist, a ``NotFoundError`` exception
        is raised."""
        vteams = self._g \
            .team_identifier(identifier, universe) \
            .elementMap() \
            .toList()

        if len(vteams) == 0:
            raise NotFoundError(identifier)
        if len(vteams) > 1:
            raise InconsistentStateError('duplicated team')

        return DbTeam.from_vteam(vteams[0])

    def add_team(self, team, universe=CURRENT_UNIVERSE):
        """Create a new team associated to the specified ``universe``. If the
        team already exists, a ``ConflictError`` exception is raised."""
        if team.identifier == '':
            raise ValueError('empty team identifier')

        if team.name == '':
            raise ValueError('empty team name')

        vteams = self._g.add_team(team, universe).toList()
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
        nteams = self._g.drop_team(vid).next()

        if nteams == 0:
            raise NotFoundError(vid)
        if nteams > 1:
            raise InconsistentStateError('duplicated team')

    # Assets.

    def assets(
        self,
        page_idx=None,
        page_size=100,
        asset_type=None,
        asset_identifier=None,
        universe=CURRENT_UNIVERSE
    ):  # pylint: disable=too-many-arguments
        """Returns all the assets belonging to the specified
        ``universe`` (filtered by ``type`` and ``identifier`` if any is
        specified) if ``page_idx`` is None. Otherwise it returns the page of
        assets with index ``page_idx`` and size ``page_size``. By default, the
        page size is 100 items."""

        vassets = self._g \
            .assets(universe, asset_type, asset_identifier)

        if page_idx is not None:
            offset = page_idx * page_size
            vassets = vassets \
                .order() \
                .by(T.id, Order.asc) \
                .range(offset, offset + page_size)

        vassets = vassets \
            .elementMap() \
            .toList()

        assets = [DbAsset.from_vasset(va) for va in vassets]
        return assets

    def asset(self, vid):
        """Returns the Asset with vertex ID ``vid``. If the asset does not
        exist, a ``NotFoundError`` exception is raised."""
        vassets = self._g \
            .asset(vid) \
            .elementMap() \
            .toList()

        if len(vassets) == 0:
            raise NotFoundError(vid)
        if len(vassets) > 1:
            raise InconsistentStateError('duplicated asset')

        return DbAsset.from_vasset(vassets[0])

    def asset_id(self, asset_id, universe=CURRENT_UNIVERSE):
        """Returns the asset with id ``asset_id`` that is linked to the given
        ``universe``. If the asset does not exist, or it exists but it's not
        linked to the given ``universe``, a ``NotFoundError`` exception is
        raised."""
        vassets = self._g \
            .asset_id(asset_id, universe=universe) \
            .elementMap() \
            .toList()

        if len(vassets) == 0:
            raise NotFoundError(asset_id)
        if len(vassets) > 1:
            raise InconsistentStateError('duplicated asset')

        return DbAsset.from_vasset(vassets[0])

    def add_asset(
         self,
         asset,
         expiration,
         timestamp=None,
         universe=CURRENT_UNIVERSE
    ):
        """Create a new asset linking it to the specified ``universe``. If the
        asset already exists, a ``ConflictError`` exception is raised. If the
        timestamp is not provided, UTC now is used."""
        if asset.asset_id.type == '' or asset.asset_id.identifier == '':
            raise ValueError('empty asset type or identifier')

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        if expiration < timestamp:
            raise ValueError('expiration before timestamp')

        vassets = self._g \
            .add_asset(
                asset,
                expiration,
                timestamp,
                universe
            ) \
            .toList()

        if len(vassets) == 0:
            raise InventoryError('asset was not created')
        if len(vassets) > 1:
            raise InconsistentStateError('duplicated asset')
        if vassets[0]['exists']:
            raise ConflictError(asset.asset_id)

        return DbAsset.from_vasset(vassets[0]['vertex'])

    def update_asset(self, vid, asset, expiration, timestamp=None):
        """Updates an asset with the specified time attributes. If the asset
        does not exist, a ``NotFoundError`` exception is raised. If the
        timestamp is not provided, UTC now is used.

        The time attributes are updated following these rules:

        - If ``timestamp < first_seen``, then ``first_seen = timestamp``.
        - If ``timestamp > last_seen``, then ``last_seen = timestamp`` and
          ``expiration = expiration``.
        - Otherwise, nothing is modified.

        Thus, an asset can be immediately invalidated with
        ``timestamp = expiration = now()``.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        if expiration < timestamp:
            raise ValueError('expiration before timestamp')

        vassets = self._g.update_asset(
            vid, asset, expiration, timestamp).toList()

        if len(vassets) == 0:
            raise NotFoundError(vid)
        if len(vassets) > 1:
            raise InconsistentStateError('duplicated asset')

        return DbAsset.from_vasset(vassets[0])

    def set_asset(
        self,
        asset,
        expiration,
        timestamp=None,
        universe=CURRENT_UNIVERSE
    ):
        """Updates an asset linked with the specified ``universe`` with the
        specified time attributes. If the asset does not exist or is not
        assciated with the universe, it is created. If the timestamp is not
        provided, UTC now is used. This function returns a tuple containing the
        vertex and a boolean that indicates if it already existed ``(DbAsset,
        bool)``.

        The time attributes are updated following these rules:

        - If ``timestamp < first_seen``, then ``first_seen = timestamp``.
        - If ``timestamp > last_seen``, then ``last_seen = timestamp`` and
          ``expiration = expiration``.
        - Otherwise, nothing is modified.

        Thus, an asset can be immediately invalidated with
        ``timestamp = expiration = now()``.
        """
        if asset.asset_id.type == '' or asset.asset_id.identifier == '':
            raise ValueError('empty asset type or identifier')

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        if expiration < timestamp:
            raise ValueError('expiration before timestamp')

        vassets = self._g. \
            set_asset(
                asset,
                expiration,
                timestamp,
                universe
            ) \
            .toList()

        if len(vassets) == 0:
            raise InventoryError('asset was not updated')
        if len(vassets) > 1:
            raise InconsistentStateError('duplicated asset')

        return (
            DbAsset.from_vasset(vassets[0]['vertex']),
            vassets[0]['exists'],
        )

    def drop_asset(self, vid):
        """Deletes the asset with vertex ID ``vid``. If the asset does not
        exist, a ``NotFoundError`` exception is raised."""
        nassets = self._g.drop_asset(vid).next()

        if nassets == 0:
            raise NotFoundError(vid)
        if nassets > 1:
            raise InconsistentStateError('duplicated asset')

    # Parents.

    def parents(self, asset_vid, page_idx=None, page_size=100):
        """Returns the list of ``DbParentOf`` of the asset with vertex ID
        ``asset_vid``. If the asset does not exist, a ``NotFoundError``
        exception is raised. If ``page_idx`` is None, all the relationships are
        returned.  Otherwise it returns the page of relationships with index
        ``page_idx`` and size ``page_size``. By default, the page size is 100
        items."""
        vassets = self._g \
            .asset(asset_vid) \
            .toList()

        if len(vassets) == 0:
            raise NotFoundError(asset_vid)
        if len(vassets) > 1:
            raise InconsistentStateError('duplicated asset')

        eparents = self._g.parents(asset_vid)

        if page_idx is not None:
            offset = page_idx * page_size
            eparents = eparents \
                .order() \
                .by(T.id, Order.asc) \
                .range(offset, offset + page_size)

        eparents = eparents \
            .elementMap() \
            .toList()

        dbparents = [DbParentOf.from_eparentof(epo) for epo in eparents]
        return dbparents

    def set_parent_of(self, parentof, expiration, timestamp=None):
        """Updates a ``parent_of`` relationship with the specified time
        attributes. If the relationship does not exist, it is created. If the
        timestamp is not provided, UTC now is used. This function returns a
        tuple containing the ``DbParentOf`` and a boolean that indicates if it
        already existed ``(DbParentOf, bool)``.

        If any of the assets does not exists, a ``NotFoundError`` exception is
        raised.

        The time attributes are updated following these rules:

        - If ``timestamp < first_seen``, then ``first_seen = timestamp``.
        - If ``timestamp > last_seen``, then ``last_seen = timestamp`` and
          ``expiration = expiration``.
        - Otherwise, nothing is modified.

        Thus, an asset can be immediately invalidated with
        ``timestamp = expiration = now()``.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Check that expiration is not before the timestamp.
        if expiration < timestamp:
            raise ValueError('expiration before timestamp')

        # Check that child and parent are not the same.
        if parentof.child_vid == parentof.parent_vid:
            raise ValueError('child_vid and parent_vid are the same')

        # Check if both vertices exist.
        vasset_child = self._g \
            .asset(parentof.child_vid) \
            .toList()
        if len(vasset_child) == 0:
            raise NotFoundError(parentof.child_vid)
        if len(vasset_child) > 1:
            raise InconsistentStateError('duplicated asset')

        vasset_parent = self._g \
            .asset(parentof.parent_vid) \
            .toList()
        if len(vasset_parent) == 0:
            raise NotFoundError(parentof.parent_vid)
        if len(vasset_parent) > 1:
            raise InconsistentStateError('duplicated asset')

        eparentof = self._g \
            .set_parent_of(parentof, expiration, timestamp) \
            .toList()

        if len(eparentof) == 0:
            raise InventoryError('parent_of was not updated')
        if len(eparentof) > 1:
            raise InconsistentStateError('duplicated edge')

        return (
            DbParentOf.from_eparentof(eparentof[0]['edge']),
            eparentof[0]['exists'],
        )

    def drop_parent_of(self, eid):
        """Deletes the ``parent_of`` edge with ID ``eid``. If the edge does not
        exist, a ``NotFoundError`` exception is raised."""
        nparentofs = self._g.drop_parent_of(eid).next()

        if nparentofs == 0:
            raise NotFoundError(eid)
        if nparentofs > 1:
            raise InconsistentStateError('duplicated edge')

    # Owners.

    def owners(self, asset_vid, page_idx=None, page_size=100):
        """Returns the list of owners (``DbOwns``) of the asset with vertex ID
        ``asset_vid``.  If the asset does not exist, a ``NotFoundError``
        exception is raised.  If ``page_idx`` is None, all the relationships
        are returned.  Otherwise it returns the page of relationships with
        index ``page_idx`` and size ``page_size``. By default, the page size is
        100 items."""
        vassets = self._g \
            .asset(asset_vid) \
            .toList()

        if len(vassets) == 0:
            raise NotFoundError(asset_vid)
        if len(vassets) > 1:
            raise InconsistentStateError('duplicated asset')

        eowners = self._g.owners(asset_vid)

        if page_idx is not None:
            offset = page_idx * page_size
            eowners = eowners \
                .order() \
                .by(T.id, Order.asc) \
                .range(offset, offset + page_size)

        eowners = eowners \
            .elementMap() \
            .toList()

        dbowners = [DbOwns.from_eowns(eo) for eo in eowners]
        return dbowners

    def set_owns(self, owns, start_time, end_time=None):
        """Updates an ``owns`` relationship with the specified time attributes.
        If the relationship does not exist, it is created. This function
        returns a tuple containing the ``DbOwns`` and a boolean that indicates
        if it already existed ``(DbOwns, bool)``.

        If the team or the asset do not exists, a ``NotFoundError`` exception
        is raised."""

        # Check that expiration is not before the timestamp.
        if end_time is not None and end_time < start_time:
            raise ValueError('end_time before start_time')

        # Check if both vertices exist.
        vteam = self._g \
            .team(owns.team_vid) \
            .toList()
        if len(vteam) == 0:
            raise NotFoundError(owns.team_vid)
        if len(vteam) > 1:
            raise InconsistentStateError('duplicated team')

        vasset = self._g \
            .asset(owns.asset_vid) \
            .toList()
        if len(vasset) == 0:
            raise NotFoundError(owns.asset_vid)
        if len(vasset) > 1:
            raise InconsistentStateError('duplicated asset')

        eowns = self._g \
            .set_owns(owns, start_time, end_time) \
            .toList()

        if len(eowns) == 0:
            raise InventoryError('owns was not updated')
        if len(eowns) > 1:
            raise InconsistentStateError('duplicated edge')

        return (
            DbOwns.from_eowns(eowns[0]['edge']),
            eowns[0]['exists'],
        )

    def drop_owns(self, eid):
        """Deletes the ``owns`` edge with ID ``eid``. If the edge does not
        exist, a ``NotFoundError`` exception is raised."""
        nowns = self._g.drop_owns(eid).next()

        if nowns == 0:
            raise NotFoundError(eid)
        if nowns > 1:
            raise InconsistentStateError('duplicated edge')

    # Universe.

    def linked_universe(self, vid):
        """Returns the universe associated with a the team or asset identified
        by ``vid``."""

        universe = self._g.linked_universe(vid).elementMap().toList()

        if len(universe) == 0:
            raise NotFoundError(vid)
        if len(universe) > 1:
            raise InconsistentStateError('duplicated universe')

        universe = universe[0]
        return DbUniverse.from_vuniverse(universe)

    def current_universe(self):
        """Returns the universe associated with the ``CURRENT_UNIVERSE``
        constant."""

        universe = self._g.universe(CURRENT_UNIVERSE).elementMap().toList()

        if len(universe) == 0:
            raise NotFoundError()
        if len(universe) > 1:
            raise InconsistentStateError('duplicated universe')

        universe = universe[0]
        return DbUniverse.from_vuniverse(universe)

    def ensure_universe(self, universe=CURRENT_UNIVERSE):
        """Ensure that there is a vertex for the specified ``universe``."""

        self._g.ensure_universe(universe).next()
