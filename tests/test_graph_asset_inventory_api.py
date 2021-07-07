"""Tests for the ``graph_asset_inventory_api`` module."""

import pytest

from graph_asset_inventory_api import EnvVarNotSetError


def test_exception_EnvVarNotSetError():  # pylint: disable=invalid-name
    """Tests the EnvVarNotSetError exception."""

    with pytest.raises(
        EnvVarNotSetError, match=r'.*ENVVAR_NAME.*'
    ) as exc_info:
        raise EnvVarNotSetError('ENVVAR_NAME')

    assert exc_info.value.name == 'ENVVAR_NAME'
