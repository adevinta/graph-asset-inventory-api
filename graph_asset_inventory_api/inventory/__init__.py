"""Provides primitives to interact with an asset inventory."""

from gremlin_python.process.traversal import T


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
        return f'<{self.vid}> {self.identifier}-{self.name}'

    def __eq__(self, o):
        return super().__eq__(o) and self.vid == o.vid

    @classmethod
    def from_vteam(cls, vteam):
        """Creates a ``DbTeam`` from a team vertex. A team vertex is the object
        returned by gremlin when using a ``elementMap`` step."""
        if str(vteam[T.label]) != 'Team':
            raise InventoryError('wrong vertex type')

        if not isinstance(vteam['identifier'], str):
            raise InventoryError('identifier is not an string')
        if not isinstance(vteam['name'], str):
            raise InventoryError('name is not an string')

        vid = vteam[T.id]
        identifier = vteam['identifier']
        name = vteam['name']

        return cls(identifier, name, vid)
