"""Provides a client module and a REST API to interact with an asset
inventory."""


class EnvVarNotSetError(Exception):
    """It is returned when an environment variable was not set."""

    def __init__(self, name=None):
        msg = 'environment variable not set'
        if name is not None:
            msg = f'environment variable not set: {name}'

        super().__init__(msg)

        self.name = name
