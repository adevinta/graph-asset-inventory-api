

class UniverseVersion:

    def __init__(self, version):
        self.int_version = UniverseVersion.__int_version(version)
        self.sem_version = version

    @classmethod
    def __int_version(cls,sem_version):
        """Returns the int representation of the universe version used to
        compare two semvers. The semver parameter must have the following
        shape: xx.xx.xx where x is a digit. That is: the major, minor and patch
        parts must be composed only by digits, and must be values from 0 to
        99"""

        if sem_version == "":
            raise SemverError()
        parts = sem_version.split(".")

        if len(parts) != 3:
            raise SemverError()
        parts.reverse()
        int_semver = 0
        for i, part in enumerate(parts):
            if len(part) > 2 or not part.isdigit():
                raise SemverError()
            int_semver = int_semver + 10 ** i * int(part)
        return int_semver

    @classmethod
    def from_int_version(cls, version):
        """Given a integer representing a semver returns the corresponding
        UniverseVersion"""
        patch = version % 10
        remainder = version // 10

        minor = remainder % 10
        remainder = remainder // 10

        major = remainder % 10

        sem_version = f"{major}.{minor}.{patch}"
        return cls(sem_version)


"""Asset Inventory Universe information"""

class CurrentUniverse:

    namespace = "asset-inventory"
    version = UniverseVersion("0.0.1")

    @classmethod
    def id(cls):
        return f"{cls.namespace}@{cls.version}"



class SemverError(Exception):
    """Returned by the semver_to_in function when the semver paramter does not
    comply with the expected shape."""

    def __init__(self):
        super().__init__(
        "the semver param must have the following shape:\ xx.xx.xx where x is a digit"
        )
