"""Tests for the ``inventory`` module."""

import pytest

from graph_asset_inventory_api.inventory import (
    NotFoundError,
    ConflictError,
)


def test_exception_NotFoundError():  # pylint: disable=invalid-name
    """Tests the NotFoundError exception."""

    with pytest.raises(
        NotFoundError, match=r'.*identifier_1337.*'
    ) as exc_info:
        raise NotFoundError('identifier_1337')

    assert exc_info.value.name == 'identifier_1337'


def test_exception_ConflictError():  # pylint: disable=invalid-name
    """Tests the ConflictError exception."""

    with pytest.raises(
        ConflictError, match=r'.*identifier_1337.*'
    ) as exc_info:
        raise ConflictError('identifier_1337')

    assert exc_info.value.name == 'identifier_1337'
