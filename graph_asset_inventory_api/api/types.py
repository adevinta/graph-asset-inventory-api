"""Collection of types used by the ``api`` module."""


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


class TeamResp(TeamReq):
    """Represents a team from the point of view of an API response."""

    def __init__(self, identifier, name, id_):
        super().__init__(identifier, name)
        self.id = id_

    def __repr__(self):
        return f'{{id: {self.id}, identifier: {self.identifier}, ' \
               f'name: {self.name}}}'

    def __str__(self):
        return f'<{self.id}> {self.identifier}-{self.name}'

    def __eq__(self, o):
        return super().__eq__(o) and self.id == o.id

    @classmethod
    def from_dbteam(cls, dbteam):
        """Creates a ``TeamResp`` from a ``DbTeam``."""
        return cls(dbteam.identifier, dbteam.name, dbteam.vid)
