"""Tests for the CurrentUniverse class ````."""

from datetime import datetime

import pytest


from graph_asset_inventory_api.inventory.universe import (
    CurrentUniverse,
    UniverseVersion,
    SemverError,
)


def test_universe_invalid_semver():
    """Tests that and exception is raised when a sem version is not valid for a
    Universe."""

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("a.a.a")

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("a.a.1")

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("a.1.1")

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("1.a.a")

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("1.1.a")

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("111.11.11")

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("11.11")

    with pytest.raises(SemverError) as exc_info:
        UniverseVersion("11")

def test_universe_from_valid_semver():
    """Tests that from a correct semversion string a proper UniverseVersion is
    constructed """

    version = UniverseVersion("0.1.1")
    assert version.sem_version == "0.1.1"
    assert version.int_version == 11

    version = UniverseVersion("1.1.2")
    assert version.sem_version == "1.1.2"
    assert version.int_version == 112

def test_universe_from_valid_intversion():
    """Tests that from a correct interger version a proper UniverseVersion is
    constructed """

    version = UniverseVersion.from_int_version(11)
    assert version.sem_version == "0.1.1"
    assert version.int_version == 11

    version = UniverseVersion.from_int_version(112)
    assert version.sem_version == "1.1.2"
    assert version.int_version == 112


def test_current_universe_is_valid():
    """Tests that the current defined Universe class is valid"""

    assert isinstance(CurrentUniverse.version, UniverseVersion)
    assert  CurrentUniverse.namespace is not None
