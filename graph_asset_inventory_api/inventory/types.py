from gremlin_python.process.traversal import T


class InventoryException(Exception):
    pass


class NotFoundException(InventoryException):
    pass


class InconsistentStateException(InventoryException):
    pass


class Team:
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
        if str(vteam[T.label]) != 'Team':
            raise InventoryException('wrong vertex type')

        if not isinstance(vteam['identifier'], str):
            raise InventoryException('identifier is not an string')
        if not isinstance(vteam['name'], str):
            raise InventoryException('name is not an string')

        vid = vteam[T.id]
        identifier = vteam['identifier']
        name = vteam['name']

        return cls(identifier, name, vid)
