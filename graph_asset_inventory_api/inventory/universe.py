"""This modules provides the class ``CURRENT_UNIVERSE`` that defines the
information about the current version of the asset inventory universe."""


from graph_asset_inventory_api.inventory import CURRENT_UNIVERSE_VERSION


class UniverseVersion:
    """Represents a version of a Universe."""

    def __init__(self, version):
        """Inits UniverseVersion with a version string. The version parameter
        must be a string with the following shape: x.x.x, where x is an
        interger between 0 and 99."""
        self._int_version = UniverseVersion._version_to_int(version)
        self._sem_version = version

    @property
    def int_version(self):
        """Returns the interger representation of the version"""
        return self._int_version

    @property
    def sem_version(self):
        """Returns the string representation of the version"""
        return self._sem_version

    @classmethod
    def _version_to_int(cls, version):
        """Returns the integer representation of the universe version used to
        compare two different versions of a universe. The version parameter
        must have the following shape: x.x.x, where x is an integer between 0
        and 99."""

        if version == "":
            raise SemverError()
        parts = version.split(".")

        if len(parts) != 3:
            raise SemverError()
        parts.reverse()
        int_semver = 0
        for i, part in enumerate(parts):
            if len(part) > 2 or not part.isdigit():
                raise SemverError()
            int_semver = int_semver + 100 ** i * int(part)
        return int_semver

    @classmethod
    def from_int_version(cls, version):
        """Given a integer representing a semver returns the corresponding
        UniverseVersion"""
        patch = version % 100
        remainder = version // 100

        minor = remainder % 100
        remainder = remainder // 100

        major = remainder % 100

        sem_version = f"{major}.{minor}.{patch}"
        return cls(sem_version)


class SemverError(Exception):
    """Returned when creating an instance of the UniverseVersion class if the
    passed version parameter does not comply with the expected shape."""

    def __init__(self):
        super().__init__(
            "the semver param must have the following shape: xx.xx.xx \
            where x is a digit"
        )


class Universe:
    """Asset Inventory Universe"""

    def __init__(self, version):
        self.namespace = "asset-inventory"
        self.version = version


CURRENT_UNIVERSE = Universe(UniverseVersion(CURRENT_UNIVERSE_VERSION))
