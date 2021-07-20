"""Provides primitives to interact with an asset inventory."""

from datetime import datetime

from gremlin_python.process.traversal import (
    T,
    Direction,
)


class InventoryError(Exception):
    """Represents a generic Asset Inventory error."""


class NotFoundError(InventoryError):
    """It is returned when a specific entity could not be found in the
    inventory."""

    def __init__(self, name=None):
        msg = 'not found'
        if name is not None:
            msg = f'not found: {name}'

        super().__init__(msg)

        self.name = name


class ConflictError(InventoryError):
    """It is returned when there is a conflict with the entity to be created.
    For instance, when trying to create a Team with the same identifier."""

    def __init__(self, name=None):
        msg = 'conflict'
        if name is not None:
            msg = f'conflict: {name}'

        super().__init__(msg)

        self.name = name


class InconsistentStateError(InventoryError):
    """It is returned when a inconsistency is detected in the Asset Inventory
    state."""


class Team:
    """Represents a Team."""

    def __init__(self, identifier, name):
        self.identifier = identifier
        self.name = name

    def __repr__(self):
        return f'{{identifier: {self.identifier}, name: {self.name}}}'

    def __str__(self):
        return f'{self.identifier}-{self.name}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False

        return self.identifier == o.identifier and self.name == o.name


class DbTeam(Team):
    """Represents a ``Team`` in the context of the Security Graph. The main
    difference with a ``Team`` is that a ``DbTeam`` has a vertex ID field."""

    def __init__(self, identifier, name, vid):
        super().__init__(identifier, name)
        self.vid = vid

    def __repr__(self):
        return f'{{vid: {self.vid}, identifier: {self.identifier}, ' \
               f'name: {self.name}}}'

    def __str__(self):
        return f'{self.identifier}-{self.name}@{self.vid}'

    def __eq__(self, o):
        return super().__eq__(o) and self.vid == o.vid

    @classmethod
    def from_vteam(cls, vteam):
        """Creates a ``DbTeam`` from a team vertex. A team vertex is the object
        returned by gremlin when using a ``elementMap`` step."""
        if vteam[T.label] != 'Team':
            raise InventoryError('wrong vertex type')

        if not isinstance(vteam['identifier'], str):
            raise InventoryError('identifier is not a string')
        if not isinstance(vteam['name'], str):
            raise InventoryError('name is not a string')

        vid = vteam[T.id]
        identifier = vteam['identifier']
        name = vteam['name']

        return cls(identifier, name, vid)


class AssetID:
    """Represents an Asset identifier."""

    def __init__(self, type_, identifier):
        self.type = type_
        self.identifier = identifier

    def __repr__(self):
        return f'{{type: {self.type}, identifier: {self.identifier}}}'

    def __str__(self):
        return f'{self.type}-{self.identifier}'

    def __hash__(self):
        return hash((self.type, self.identifier))

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False

        return self.type == o.type and self.identifier == o.identifier


class AssetTimeAttr:
    """Represents the time attributes associated with an Asset. They can belong
    to the asset itself or to a ``parent_of`` relationship."""

    def __init__(self, first_seen, last_seen, expiration):
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.expiration = expiration

    def __repr__(self):
        return f'{{first_seen: {self.first_seen}, ' \
               f'last_seen: {self.last_seen}, ' \
               f'expiration: {self.expiration}}}'

    def __str__(self):
        return f'({self.first_seen}, {self.last_seen}, {self.expiration})'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False

        return self.first_seen == o.first_seen and \
            self.last_seen == o.last_seen and self.expiration == o.expiration


class Asset:
    """Represents an Asset."""

    def __init__(self, asset_id):
        self.asset_id = asset_id

    def __repr__(self):
        return f'{{asset_id: {self.asset_id}}}'

    def __str__(self):
        return f'{self.asset_id}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False

        return self.asset_id == o.asset_id


class DbAsset(Asset):
    """Represents an ``Asset`` in the context of the Security Graph. The main
    difference with an ``Asset`` is that a ``DbAsset`` has time attributes and
    a vertex ID."""

    def __init__(self, asset_id, vid, time_attr):
        super().__init__(asset_id)
        self.vid = vid
        self.time_attr = time_attr

    def __repr__(self):
        return f'{{vid: {self.vid}, asset_id: {self.asset_id}, ' \
               f'time_attr: {self.time_attr}}}'

    def __str__(self):
        return f'{self.asset_id}@{self.vid}'

    def __eq__(self, o):
        return super().__eq__(o) and self.vid == o.vid and \
            self.time_attr == o.time_attr

    @classmethod
    def from_vasset(cls, vteam):
        """Creates a ``DbAsset`` from an asset vertex. An asset vertex is the
        object returned by gremlin when using a ``elementMap`` step."""
        if vteam[T.label] != 'Asset':
            raise InventoryError('wrong vertex type')

        if not isinstance(vteam['type'], str):
            raise InventoryError('type is not an string')
        if not isinstance(vteam['identifier'], str):
            raise InventoryError('identifier is not an string')
        if not isinstance(vteam['first_seen'], datetime):
            raise InventoryError('first_seen is not a datetime')
        if not isinstance(vteam['last_seen'], datetime):
            raise InventoryError('last_seen is not a datetime')
        if not isinstance(vteam['expiration'], datetime):
            raise InventoryError('expiration is not a datetime')

        vid = vteam[T.id]
        asset_id = AssetID(vteam['type'], vteam['identifier'])

        first_seen = vteam['first_seen']
        last_seen = vteam['last_seen']
        expiration = vteam['expiration']
        time_attr = AssetTimeAttr(first_seen, last_seen, expiration)

        return cls(asset_id, vid, time_attr)


class ParentOf:
    """Represents a ``parent_of`` relationship."""

    def __init__(self, parent_vid, child_vid):
        self.parent_vid = parent_vid
        self.child_vid = child_vid

    def __repr__(self):
        return f'{{parent_vid: {self.parent_vid}, ' \
               f'child_vid: {self.child_vid}}}'

    def __str__(self):
        return f'{self.parent_vid} -parent_of-> {self.child_vid}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False

        return self.parent_vid == o.parent_vid and \
            self.child_vid == o.child_vid


class DbParentOf(ParentOf):
    """Represents a ``parent_of`` relationship in the context of the Security
    Graph. The main difference with a ``ParentOf`` is that a ``DbParentOf`` has
    an edge ID ``eid`` and time attributes."""

    def __init__(self, parent_vid, child_vid, eid, time_attr):
        super().__init__(parent_vid, child_vid)
        self.eid = eid
        self.time_attr = time_attr

    def __repr__(self):
        return f'{{eid: {self.eid}, parent_vid: {self.parent_vid}, ' \
                f'child_vid: {self.child_vid}, time_attr: {self.time_attr}}}'

    def __str__(self):
        return f'{self.parent_vid}-parent_of@{self.eid}->{self.child_vid}'

    def __eq__(self, o):
        return super().__eq__(o) and self.eid == o.eid and \
            self.eid == o.eid and self.time_attr == o.time_attr

    @classmethod
    def from_eparentof(cls, eparentof):
        """Creates a ``DbParentOf`` from a ``parent_of`` edge. A ``parent_of``
        edge is the object returned by gremlin when using a ``elementMap``
        step."""
        if eparentof[T.label] != 'parent_of':
            raise InventoryError('wrong edge type')

        if not isinstance(eparentof['first_seen'], datetime):
            raise InventoryError('first_seen is not a datetime')
        if not isinstance(eparentof['last_seen'], datetime):
            raise InventoryError('last_seen is not a datetime')
        if not isinstance(eparentof['expiration'], datetime):
            raise InventoryError('expiration is not a datetime')

        eid = eparentof[T.id]
        parent_vid = eparentof[Direction.OUT][T.id]
        child_vid = eparentof[Direction.IN][T.id]

        first_seen = eparentof['first_seen']
        last_seen = eparentof['last_seen']
        expiration = eparentof['expiration']
        time_attr = AssetTimeAttr(first_seen, last_seen, expiration)

        return cls(parent_vid, child_vid, eid, time_attr)


class TeamTimeAttr:
    """Represents the time attributes associated with a Team and, specifically,
    with an ``owns`` relationship."""

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f'{{start_time: {self.start_time}, end_time: {self.end_time}}}'

    def __str__(self):
        return f'({self.start_time}, {self.end_time})'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False

        return self.start_time == o.start_time and \
            self.end_time == o.end_time


class Owns:
    """Represents an ``owns`` relationship."""

    def __init__(self, team_vid, asset_vid):
        self.team_vid = team_vid
        self.asset_vid = asset_vid

    def __repr__(self):
        return f'{{team_vid: {self.team_vid}, asset_vid: {self.asset_vid}}}'

    def __str__(self):
        return f'{self.team_vid} -owns-> {self.asset_vid}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False

        return self.team_vid == o.team_vid and \
            self.asset_vid == o.asset_vid


class DbOwns(Owns):
    """Represents an ``owns`` relationship in the context of the Security
    Graph. The main difference with an ``Owns`` is that a ``DbOwns`` has an
    edge ID ``eid`` and time attributes."""

    def __init__(self, team_vid, asset_vid, eid, time_attr):
        super().__init__(team_vid, asset_vid)
        self.eid = eid
        self.time_attr = time_attr

    def __repr__(self):
        return f'{{eid: {self.eid}, team_vid: {self.team_vid}, ' \
                f'asset_vid: {self.asset_vid}, time_attr: {self.time_attr}}}'

    def __str__(self):
        return f'{self.team_vid}-owns@{self.eid}->{self.asset_vid}'

    def __eq__(self, o):
        return super().__eq__(o) and self.eid == o.eid and \
            self.eid == o.eid and self.time_attr == o.time_attr

    @classmethod
    def from_eowns(cls, eowns):
        """Creates a ``DbOwns`` from an ``owns`` edge. An ``owns`` edge is the
        object returned by gremlin when using a ``elementMap`` step."""
        if eowns[T.label] != 'owns':
            raise InventoryError('wrong edge type')

        if not isinstance(eowns['start_time'], datetime):
            raise InventoryError('start_time is not a datetime')
        if not isinstance(eowns['end_time'], datetime):
            raise InventoryError('end_time is not a datetime')

        eid = eowns[T.id]
        team_vid = eowns[Direction.OUT][T.id]
        asset_vid = eowns[Direction.IN][T.id]

        start_time = eowns['start_time']
        end_time = eowns['end_time']
        time_attr = TeamTimeAttr(start_time, end_time)

        return cls(team_vid, asset_vid, eid, time_attr)
