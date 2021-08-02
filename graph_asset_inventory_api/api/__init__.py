"""Provides a REST API to interact with an asset inventory."""


# Teams.


class TeamReq:
    """Represents a team from the point of view of an API request."""

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


class TeamResp:
    """Represents a team from the point of view of an API response."""

    def __init__(self, id_, identifier, name):
        self.id = id_
        self.identifier = identifier
        self.name = name

    def __repr__(self):
        return f'{{id: {self.id}, identifier: {self.identifier}, ' \
               f'name: {self.name}}}'

    def __str__(self):
        return f'{self.identifier}-{self.name}@{self.id}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False
        return self.id == o.id and self.identifier == o.identifier and \
            self.name == o.name

    @classmethod
    def from_dbteam(cls, dbteam):
        """Creates a ``TeamResp`` from a ``DbTeam``."""
        return cls(dbteam.vid, dbteam.identifier, dbteam.name)


# Assets.


class AssetReq:
    """Represents an asset from the point of view of an API request."""

    def __init__(self, asset_id, timestamp, expiration):
        self.type = asset_id.type
        self.identifier = asset_id.identifier
        self.timestamp = timestamp.isoformat()
        self.expiration = expiration.isoformat()

    def __repr__(self):
        return f'{{type: {self.type}, identifier: {self.identifier}, ' \
               f'timestamp: {self.timestamp}, expiration: {self.expiration}}}'

    def __str__(self):
        return f'{self.type}-{self.identifier}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False
        return self.type == o.type and self.identifier == o.identifier and \
            self.timestamp == o.timestamp and self.expiration == o.expiration


class AssetResp:
    """Represents an asset from the point of view of an API response."""

    def __init__(self, id_, asset_id, time_attr):
        self.id = id_
        self.type = asset_id.type
        self.identifier = asset_id.identifier
        self.first_seen = time_attr.first_seen.isoformat()
        self.last_seen = time_attr.last_seen.isoformat()
        self.expiration = time_attr.expiration.isoformat()

    def __repr__(self):
        return f'{{id: {self.id}, type: {self.type}, ' \
               f'identifier: {self.identifier}, ' \
               f'first_seen: {self.first_seen}, ' \
               f'last_seen: {self.last_seen}, ' \
               f'expiration: {self.expiration}}}'

    def __str__(self):
        return f'{self.type}-{self.identifier}@{self.id}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False
        return self.id == o.id and self.type == o.type and \
            self.identifier == o.identifier and \
            self.first_seen == o.first_seen and \
            self.last_seen == o.last_seen and \
            self.expiration == o.expiration

    @classmethod
    def from_dbasset(cls, dbasset):
        """Creates an ``AssetResp`` from a ``DbAsset``."""
        return cls(dbasset.vid, dbasset.asset_id, dbasset.time_attr)


# Parents.


class ParentOfReq:
    """Represents a ``parent_of`` relationship from the point of view of an API
    request."""

    def __init__(self, timestamp, expiration):
        self.timestamp = timestamp.isoformat()
        self.expiration = expiration.isoformat()

    def __repr__(self):
        return f'{{timestamp: {self.timestamp}, ' \
               f'expiration: {self.expiration}}}'

    def __str__(self):
        return f'({self.timestamp}, {self.expiration})'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False
        return self.timestamp == o.timestamp and \
            self.expiration == o.expiration


class ParentOfResp:
    """Represents a ``parent_of`` relationship from the point of view of an API
    response."""

    def __init__(self, id_, parent_id, child_id, time_attr):
        self.id = id_
        self.parent_id = parent_id
        self.child_id = child_id
        self.first_seen = time_attr.first_seen.isoformat()
        self.last_seen = time_attr.last_seen.isoformat()
        self.expiration = time_attr.expiration.isoformat()

    def __repr__(self):
        return f'{{id: {self.id}, ' \
               f'parent_id: {self.parent_id}, ' \
               f'child_id: {self.child_id}, ' \
               f'first_seen: {self.first_seen}, ' \
               f'last_seen: {self.last_seen}, ' \
               f'expiration: {self.expiration}}}'

    def __str__(self):
        return f'{self.parent_id}-parent_of->{self.child_id}@{self.id}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False
        return self.id == o.id and \
            self.parent_id == o.parent_id and \
            self.child_id == o.child_id and \
            self.first_seen == o.first_seen and \
            self.last_seen == o.last_seen and \
            self.expiration == o.expiration

    @classmethod
    def from_dbparentof(cls, dbparentof):
        """Creates a ``ParentOfResp`` from a ``DbParentOf``."""
        return cls(
            dbparentof.eid,
            dbparentof.parent_vid,
            dbparentof.child_vid,
            dbparentof.time_attr,
        )


# Owners.


class OwnsReq:
    """Represents an ``owns`` relationship from the point of view of an API
    request."""

    def __init__(self, time_attr):
        self.start_time = time_attr.start_time.isoformat()
        self.end_time = None
        if time_attr.end_time is not None:
            self.end_time = time_attr.end_time.isoformat()

    def __repr__(self):
        return f'{{start_time: {self.start_time}, end_time: {self.end_time}}}'

    def __str__(self):
        return f'({self.start_time}, {self.end_time})'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False
        return self.start_time == o.start_time and self.end_time == o.end_time


class OwnsResp:
    """Represents an ``owns`` relationship from the point of view of an API
    response."""

    def __init__(self, id_, team_id, asset_id, time_attr):
        self.id = id_
        self.team_id = team_id
        self.asset_id = asset_id
        self.start_time = time_attr.start_time.isoformat()
        self.end_time = None
        if time_attr.end_time is not None:
            self.end_time = time_attr.end_time.isoformat()

    def __repr__(self):
        return f'{{id: {self.id}, ' \
               f'team_id: {self.team_id}, ' \
               f'asset_id: {self.asset_id}, ' \
               f'start_time: {self.start_time}, ' \
               f'end_time: {self.end_time}}}'

    def __str__(self):
        return f'{self.team_id}-owns->{self.asset_id}@{self.id}'

    def __eq__(self, o):
        if not isinstance(self, o.__class__):
            return False
        return self.id == o.id and \
            self.team_id == o.team_id and \
            self.asset_id == o.asset_id and \
            self.start_time == o.start_time and \
            self.end_time == o.end_time

    @classmethod
    def from_dbowns(cls, dbowns):
        """Creates a ``OwnsResp`` from a ``DbOwns``."""
        return cls(
            dbowns.eid,
            dbowns.team_vid,
            dbowns.asset_vid,
            dbowns.time_attr,
        )
