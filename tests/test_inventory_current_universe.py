"""Tests for the ``CURRENT_UNIVERSE`` class."""

import pytest


from graph_asset_inventory_api.inventory.universe import (
    CURRENT_UNIVERSE,
    UniverseVersion,
    SemverError,
)


def test_universe_invalid_semver():
    """Tests that and exception is raised when a sem version is not valid for a
    Universe."""

    with pytest.raises(SemverError):
        UniverseVersion("a.a.a")

    with pytest.raises(SemverError):
        UniverseVersion("a.a.1")

    with pytest.raises(SemverError):
        UniverseVersion("a.1.1")

    with pytest.raises(SemverError):
        UniverseVersion("1.a.a")

    with pytest.raises(SemverError):
        UniverseVersion("1.1.a")

    with pytest.raises(SemverError):
        UniverseVersion("111.11.11")

    with pytest.raises(SemverError):
        UniverseVersion("11.11")

    with pytest.raises(SemverError):
        UniverseVersion("11")


def test_universe_from_valid_semver():
    """Tests that from a correct semversion string a proper ``UniverseVersion``
    is constructed."""

    version = UniverseVersion("0.1.1")
    assert version.sem_version == "0.1.1"
    assert version.int_version == 101

    version = UniverseVersion("1.1.2")
    assert version.sem_version == "1.1.2"
    assert version.int_version == 10102


def test_universe_from_valid_intversion():
    """Tests that from a correct interger version a proper ``UniverseVersion`` is
    constructed."""

    version = UniverseVersion.from_int_version(11)
    assert version.sem_version == "0.0.11"
    assert version.int_version == 11

    version = UniverseVersion.from_int_version(10102)
    assert version.sem_version == "1.1.2"
    assert version.int_version == 10102


def test_current_universe_is_valid():
    """Tests that the current defined Universe is valid."""

    assert isinstance(CURRENT_UNIVERSE.version, UniverseVersion)
    assert CURRENT_UNIVERSE.namespace is not None


def test_universe_int_version_collision():
    """Tests that two different semver strings do not generate the same
    ``int_version``."""

    version_a = UniverseVersion("0.2.1")
    version_b = UniverseVersion("0.0.21")
    assert version_a.int_version != version_b.int_version
